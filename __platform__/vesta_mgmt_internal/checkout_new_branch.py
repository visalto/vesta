import logging
from pathlib import Path

import git

logger = logging.getLogger(__name__)


def new_branch(branch_name: str) -> None:
    # Get repo location
    current_dir = Path(__file__).resolve().parent
    repo_dir = current_dir.parent.parent
    logger.info(f'Repo loc {repo_dir.__str__()}')

    # Define the name of the new branch
    new_branch_name = branch_name

    # Switch the main repository to the new branch
    repo = git.Repo(repo_dir.__str__())
    repo.git.checkout("-b", new_branch_name)
    origin = repo.remote(name="origin")
    origin.push(refspec="{}:{}".format(new_branch_name, new_branch_name))

    # Loop through all submodules and switch them to the new branch
    for submodule in repo.submodules:
        submodule_repo = submodule.module()
        submodule_repo.git.checkout("-b", new_branch_name)
        origin = submodule_repo.remote(name="origin")
        origin.push(refspec="{}:{}".format(new_branch_name, new_branch_name))
        logger.info(f'Submodule {submodule} checked out and switched to new branch {new_branch_name}')

    # Update all submodules to the latest commit on the new branch
    logger.info('Updating all submodules to the latest commit on the new branch')
    repo.git.submodule("update", "--recursive", "--remote")

    logger.info(f'Success! vesta and all submodules are now working from branch {new_branch_name}')


if __name__ == '__main__':
    new_branch('stef')
