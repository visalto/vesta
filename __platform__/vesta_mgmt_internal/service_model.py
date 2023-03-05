"""
Python Model representation of vesta service.
Vesta service represent module in vesta repository.
Example services: vesta-lineage, vesta-git, vesta-airflow etc.
"""
from pathlib import Path
import os
import logging
import fnmatch
from typing import List, Union
from datetime import datetime
from dotenv import load_dotenv

import docker

logger = logging.getLogger(__name__)


def _run_cmd(cmd: str, on_success_msg: str, on_error_msg: str, fail_gracefully: bool = False) -> None:
    exit_code = os.system(cmd)
    if exit_code == 0:
        logger.info(on_success_msg)
    else:
        logger.warning(on_error_msg)
        if not fail_gracefully:
            raise RuntimeError(f'Command failed with exit code {exit_code}. {on_error_msg}')


class VestaService:
    def __init__(self, service_path: Union[Path, str], base_dir: str, env_file: str):
        self.path = Path(service_path).resolve()
        self.BASE_DIR = base_dir
        self.ENV_FILE = env_file
        self.name = self.path.parts[len(self.path.parts) - 1]
        self.dir_str = None
        # Run checks for vesta service to make sure
        # it is initialized properly and all underlying
        # components are present
        checks = [self.check_if_module_exist, self.check_if_docker_compose_exist]
        for service_check in checks:
            logger.info(f'{service_check.__name__} running...')
            service_check()

    def check_if_module_exist(self):
        if not self.path.exists():
            raise RuntimeError('Service module cannot be found')
        logger.info(f'{self.name} module present')
        self.dir_str = self.path.__str__()

    def check_if_docker_compose_exist(self):
        compose_file_name = 'docker-compose.yml'
        is_file_present = compose_file_name in os.listdir(self.path)
        if not is_file_present:
            raise RuntimeError(f'docker-compose not found in service module {self.name}')

        logger.info(f'{self.name} docker-compose present')

    def start(self, force_build: bool = False):
        command = "" \
                  f"cd {self.dir_str} &&" \
                  f"docker-compose --env-file {self.ENV_FILE.__str__()} up -d"
        if force_build:
            command += ' --build'
        _run_cmd(command, f'{self.name} service started successfully', f'{self.name} error starting up')

    def stop(self):
        logger.info(f'Stopping service {self.name}')
        # format docker compose command
        command = "" \
                  f"cd {self.dir_str} &&" \
                  f"docker-compose --env-file {self.ENV_FILE.__str__()} down"
        _run_cmd(command, f'{self.name} service stopped successfully', f'Error stopping {self.name}')


class Vesta:
    VESTAIGNORE_FILE_NAME = '.vestaignore'
    UTIL_SERVICES_SUBMODULE = 'util-services'

    def __init__(self, base_dir: Path):
        self.BASE_DIR = base_dir
        self.ENV_FILE = self.BASE_DIR.joinpath('.env').resolve()
        self.services = self.scan_service_list()

        if not self.ENV_FILE:
            raise FileNotFoundError('.env is missing from root Vesta repo. Check this doc for more info')

    def start_services(self, force_build: bool = False):
        logger.info('Vesta start signal received..')
        self._logger_util('Parameters summary before deployment process begins')
        self.check_or_crete_network()
        logger.info('Deploying platform components...')
        for service in self.services:
            service.start(force_build)
        logger.info('All components have been deployed')
        logo_path = self.BASE_DIR.joinpath('__platform__/vesta_mgmt_internal/vesta_cmd_ascii.txt').resolve()
        if logo_path.exists():
            os.system(f'type {logo_path.__str__()}')
        logger.info('Platform url: {}')

    def _logger_util(self, header: str):
        logger.info('|--------------------------------------------|')
        logger.info(f'{header}')
        logger.info(f'--No. Of Modules:    {len(self.services)}')
        logger.info(f'--------BASE_DIR:    {self.BASE_DIR}')
        logger.info(f'--------ENV_FILE:    {self.ENV_FILE}')
        logger.info('|--------------------------------------------|')

    def stop_services(self):
        logger.info('Stop signal received')
        self._logger_util('Parameters summary before stop process begins:')
        for service in self.services:
            service.stop()
        logger.info('All components have been stopped and removed')
        logger.info(f'Platform shut down - {datetime.now.__str__()}')

    def _parse_vestaignore(self) -> List[str]:
        vestaignore = self.VESTAIGNORE_FILE_NAME
        service_list_to_ignore = []
        with open(self.BASE_DIR.joinpath(vestaignore)) as f:
            for service in f:
                service = service.strip()
                if not service or service.startswith('#'):
                    continue

                service_list_to_ignore.append(service)
        return service_list_to_ignore

    def scan_service_list(self) -> List[VestaService]:
        base_dir_list = os.listdir(BASE_DIR)
        vesta_ignore = self._parse_vestaignore()
        util_services = self.UTIL_SERVICES_SUBMODULE
        services_list = []
        for root_item in base_dir_list:
            is_util_services = root_item == util_services
            root_item_path: Path = BASE_DIR.joinpath(root_item)
            if is_util_services:
                for util_service in os.listdir(BASE_DIR.joinpath(root_item)):
                    util_service_path: Path = root_item_path.joinpath(util_service)
                    is_util_service_in_ignore = True in [fnmatch.fnmatch(f'{root_item}/{util_service}', i) for i in
                                                         vesta_ignore]
                    if not is_util_service_in_ignore:
                        services_list.append(util_service_path)
            else:
                is_item_in_ignore = root_item in vesta_ignore
                is_glob_pattern_matching = True in [fnmatch.fnmatch(root_item, i) for i in vesta_ignore]
                if not is_item_in_ignore and not is_glob_pattern_matching:
                    services_list.append(root_item_path)
        parsed = [VestaService(i, self.BASE_DIR, self.ENV_FILE) for i in services_list]
        return parsed

    def service(self, service_name: str) -> VestaService:
        return VestaService(self.BASE_DIR.joinpath(service_name), self.BASE_DIR, self.ENV_FILE)

    def check_or_crete_network(self):
        is_env_loaded = load_dotenv(self.ENV_FILE)
        if not is_env_loaded:
            raise EnvironmentError('.env is not loaded properly')
        client = docker.from_env()
        networks = [i.name for i in client.networks.list()]
        vesta_network = os.environ.get('DOCKER_NETWORK_NAME')
        is_network_present = vesta_network in networks
        if not is_network_present:
            logger.info(f'Network is missing. Creating {vesta_network} network')
            client.networks.create(vesta_network)
            logger.info('Network created successfully')


if __name__ == '__main__':
    logging.basicConfig(level='INFO')
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    platform = Vesta(BASE_DIR)
    platform.stop_services()
    # git_service = platform.service('vesta-git')
    # platform_web = platform.service('vesta-platform-core')
    # platform_web.start()
    # git_service.start()
    print('')