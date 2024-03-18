"""
Python Model representation of vesta service.
Vesta service represent module in vesta repository.
Example services: vesta-lineage, vesta-git, vesta-airflow etc.
"""
import fnmatch
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List, Union

import docker
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def _run_cmd(cmd: str, on_success_msg: str, on_error_msg: str, fail_gracefully: bool = False) -> None:
    exit_code = os.system(cmd)
    if exit_code == 0:
        logger.info(on_success_msg)
    else:
        logger.warning(on_error_msg)
        if not fail_gracefully:
            raise RuntimeError(
                f'Command failed with exit code {exit_code}. {on_error_msg}')


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
        checks = [self.check_if_module_exist,
                  self.check_if_docker_compose_exist]
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
            raise RuntimeError(
                f'docker-compose not found in service module {self.name}')

        logger.info(f'{self.name} docker-compose present')

    def start(self, force_build: bool = False):
        command = "" \
                  f"cd {self.dir_str} &&" \
                  f"docker-compose --env-file {self.ENV_FILE.__str__()} up -d"
        if force_build:
            command += ' --build'
        fail_gracefully = True if self.name == 'vesta-platform-core' else False
        _run_cmd(command, f'{self.name} service started successfully',
                 f'{self.name} finished starting up with non zero code', fail_gracefully=fail_gracefully)

    def stop(self):
        logger.info(f'Stopping service {self.name}')
        # format docker compose command
        command = "" \
                  f"cd {self.dir_str} &&" \
                  f"docker-compose --env-file {self.ENV_FILE.__str__()} down"
        _run_cmd(command, f'{self.name} service stopped successfully',
                 f'Error stopping {self.name}')


class Vesta:
    VESTAIGNORE_FILE_NAME = '.vestaignore'
    UTIL_SERVICES_SUBMODULE = 'util-services'
    SERVICES_PRIORITY = ['vesta-airflow',
                         'vesta-git',
                         'vesta-platform-core']

    def __init__(self, base_dir: Path):
        self.BASE_DIR = base_dir
        self.ENV_FILE = self.BASE_DIR.joinpath('.env').resolve()
        self.services = self.scan_service_list()

        if not self.ENV_FILE:
            raise FileNotFoundError(
                '.env is missing from root Vesta repo')

    def start_services(self, force_build: bool = False):
        logger.info('Vesta start signal received..')
        self._logger_util(
            'Parameters summary before deployment process begins')
        self.check_or_crete_network()
        logger.info('Deploying platform components...')

        for service in self.services:
            service.start(force_build)
        logger.info('All components have been deployed')
        logo_path = self.BASE_DIR.joinpath(
            '__platform__/vesta_mgmt_internal/vesta_cmd_ascii.txt').resolve()
        if logo_path.exists():
            os.system(f'cat {logo_path.__str__()}')
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
        # Get the list of items in the base directory.
        base_dir_list = os.listdir(self.BASE_DIR)

        # Parse the 'vestaignore' file to get the list of patterns to ignore.
        vesta_ignore = self._parse_vestaignore()

        # Set the 'util_services' variable to the UTIL_SERVICES_SUBMODULE value.
        util_services = self.UTIL_SERVICES_SUBMODULE

        # Create an empty list to store the services that will be processed.
        services_list = []

        # Loop through each item in the base directory.
        for root_item in base_dir_list:

            # Check if the current item is the UTIL_SERVICES_SUBMODULE.
            is_util_services = root_item == util_services

            # Create a Path object for the current root item.
            root_item_path: Path = self.BASE_DIR.joinpath(root_item)

            # If the current item is the UTIL_SERVICES_SUBMODULE, process its contents.
            if is_util_services:
                # Loop through each item in the UTIL_SERVICES_SUBMODULE directory.
                for util_service in os.listdir(self.BASE_DIR.joinpath(root_item)):
                    # Create a Path object for the current util_service item.
                    util_service_path: Path = root_item_path.joinpath(
                        util_service)

                    # Check if the current util_service item matches any pattern in the 'vestaignore' list.
                    is_util_service_in_ignore = True in [fnmatch.fnmatch(
                        f'{root_item}/{util_service}', i) for i in vesta_ignore]

                    # If the util_service item is not in the 'vestaignore' list, add it to the services_list.
                    if not is_util_service_in_ignore:
                        services_list.append(util_service_path)
            else:
                # Check if the current item should be ignored based on an exact match with 'vestaignore'.
                is_item_in_ignore = root_item in vesta_ignore

                # Check if the current item matches any pattern in the 'vestaignore' list.
                is_glob_pattern_matching = True in [
                    fnmatch.fnmatch(root_item, i) for i in vesta_ignore]

                # If the item is not in the 'vestaignore' list (exact match or pattern match), add it to the services_list.
                if not is_item_in_ignore and not is_glob_pattern_matching:
                    services_list.append(root_item_path)

        # Create a list of ordered services based on the priority defined in SERVICES_PRIORITY.
        priority_services = [self.BASE_DIR.joinpath(
            i) for i in self.SERVICES_PRIORITY]
        ordered_services = priority_services + [s for s in services_list if s not in priority_services]

        # Create a list of VestaService objects for each item in the services_list, passing necessary parameters.
        parsed = [VestaService(i, self.BASE_DIR, self.ENV_FILE)
                  for i in ordered_services]

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
            logger.info(
                f'Network is missing. Creating {vesta_network} network')
            client.networks.create(vesta_network)
            logger.info('Network created successfully')


if __name__ == '__main__':
    logging.basicConfig(level='INFO')
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    platform = Vesta(BASE_DIR)
    print(platform.ENV_FILE)
    # platform.start_services()
    # platform.service('vesta-git').stop()
    # platform.service('vesta-airflow').stop()
    # platform.service('vesta-platform-core').stop()

    # platform.service('vesta-git').start(force_build=True)
    # platform.service('vesta-airflow').start(force_build=False)
    platform.service('vesta-platform-core').start(force_build=False)
    # platform.service('proxy-manager').start(force_build=False)

    print('')
