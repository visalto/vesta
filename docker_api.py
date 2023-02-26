import docker

if __name__ == '__main__':
    docker_client = docker.from_env()
    volumes = docker_client.volumes

    print('')
