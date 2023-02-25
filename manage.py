import click
import os
from typing import Union, List
from pathlib import Path
import logging
import fnmatch

logging.basicConfig(level='INFO')

logger = logging.getLogger(__name__)
VESTA = 'vesta'
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR.joinpath('.env')


def _parse_vestaignore(base_dir: Path = BASE_DIR) -> List[str]:
    vestaignore = '.vestaignore'
    service_list_to_ignore = []
    with open(base_dir.joinpath(vestaignore)) as f:
        for service in f:
            service = service.strip()
            if not service or service.startswith('#'):
                continue

            service_list_to_ignore.append(service)
    return service_list_to_ignore


def fetch_list_of_services(services_as_string: bool = False) -> Union[List[Path], List[str]]:
    base_dir_list = os.listdir(BASE_DIR)
    vesta_ignore = _parse_vestaignore()
    util_services = 'util-services'
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
    if services_as_string:
        parsed = [i.__str__() for i in services_list]
        return parsed
    return services_list


@click.command()
@click.argument('service', type=str)
@click.argument('mode', type=str)
@click.option('--build', default=False, is_flag=True, flag_value=True,
              help='Force to rebuild the image upon starting the containers')
@click.option('-f', default=False, is_flag=True, flag_value=True,
              help='Follow logs output')
def service_manager(service: str, mode: str, build: bool, f: bool):
    MODE_ALLOWED_OPTIONS = ['start', 'stop', 'logs']
    if mode not in MODE_ALLOWED_OPTIONS:
        raise ValueError(f'Invalid mode options. Options: {tuple(MODE_ALLOWED_OPTIONS)}')
    # change working directory to the service
    os.chdir(BASE_DIR.joinpath(service))
    is_start = mode == 'start'
    is_stop = mode == 'stop'
    is_logs = mode == 'logs'
    if is_start:
        start_service_docker_compose(service, build)
    if is_stop:
        stop_service_docker_compose(service)
    if is_logs:
        show_service_logs(f)


def _run_cmd(cmd: str, on_success_msg: str, on_error_msg: str) -> None:
    exit_code = os.system(cmd)
    if exit_code == 0:
        logger.info(on_success_msg)
    else:
        logger.warning(on_error_msg)
        raise RuntimeError(f'Command failed with exit code {exit_code}')
    pass


def show_service_logs(follow: bool) -> None:
    docker_cmd = 'docker-compose logs'
    if follow:
        docker_cmd += ' -f'
    _run_cmd(docker_cmd, 'Logs Fetched', 'Error fetching logs')


def start_service_docker_compose(service_name: str, build: bool):
    logger.info(f'Starting service {service_name}')
    # format docker compose command
    docker_cmd = f'docker-compose --env-file {ENV_FILE.__str__()} up -d'
    if build:
        logger.info('   Build flag detected. Will rebuild the image if there are changes')
        docker_cmd += ' --build'

    logger.info(f'running command: {docker_cmd}')
    _run_cmd(docker_cmd, 'Service started successfully', f'Error starting {service_name}')


def stop_service_docker_compose(service_name: str):
    logger.info(f'Stopping service {service_name}')
    # format docker compose command
    docker_cmd = f'docker-compose --env-file {ENV_FILE.__str__()} down'
    _run_cmd(docker_cmd, 'Service stopped successfully', f'Error stopping {service_name}')


if __name__ == '__main__':
    service_manager()
