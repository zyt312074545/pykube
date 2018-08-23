import yaml
import click
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import Validator


@click.group()
def cli():
    """Use for kubernetes, designed to automate Kubernetes workflow."""
    pass


@cli.command()
@click.option('--kind', type=click.Choice(['deployment', 'service', 'ingress']),
              prompt='? Please enter the kind of yaml', help='The kind of yaml.')
def generate(kind):
    """Use for generate kubernetes yaml file."""
    click.secho('  Begin ' + kind + ' workflow ......', fg='black', bg='green')
    if kind == 'deployment':
        generate_deploy()
    elif kind == 'service':
        pass
    else:
        pass


# validate the value is empty string
def is_null(text):
    if text:
        return True
    else:
        return False


# validate the value is digit
def is_number(text):
    return text.isdigit()


validator_null = Validator.from_callable(
    is_null,
    error_message='This input can not be empty string!',
)

validator_digit = Validator.from_callable(
    is_number,
    error_message='This input contains non-numeric characters!',
)


def str2list(string):
    str_list = string.split(' ')
    while '' in str_list:
        str_list.remove('')
    return str_list


def generate_deploy():
    """
    Generate deploy yaml file, need follow parameters:
        - deployment name
        - deployment labels (this is use for service)
        - replica number
        - containers information
        - restart policy
    """

    # deployment template
    deploy = {
        "apiVersion": "extensions/v1beta1",
        "kind": "Deployment",
        "metadata": {},
        "spec": {"replicas": 1, "template": {"metadata": {}, "spec": {"containers": []}}}
    }

    # add name
    name = prompt(FormattedText([('#B58900', '? Please enter the name of deployment: ')]), validator=validator_null)
    deploy["metadata"]["name"] = name

    # add replicas
    replica = prompt(FormattedText([('#B58900', '? Please enter the number of replica: ')]), validator=validator_digit)
    deploy["spec"]["replicas"] = int(replica)

    # add labels
    click.secho(
        "? Please enter the labels, this is useful for service (if more than one, use space, like 'A B'): ",
        fg='yellow')
    labels_key = prompt("  ? Name of labels: ", validator=validator_null)
    labels_value = prompt('  ? Value of labels: ', validator=validator_null)
    if len(str2list(labels_key)) != len(str2list(labels_value)):
        click.secho("! The key's number of labels not equal to value's number, please try again.", fg='red')
    else:
        deploy["spec"]["template"]["metadata"]["labels"] = dict(zip(str2list(labels_key), str2list(labels_value)))

        # add container include of basic and special info
        # add basic info
        click.secho('? Please enter the containers information (if more than one, use space): ', fg='yellow')
        container_name = prompt('  ? Name of container: ', validator=validator_null)
        container_image = prompt('  ? Image of container: ', validator=validator_null)
        container_port = prompt('  ? Port of container: ', validator=validator_null)
        port_list = []
        for i in str2list(container_port):
            try:
                i = int(i)
            except:
                click.secho("! The port is not digit, please try again.", fg='red')
                click.Context.exit(0)
            port_list.append({"containerPort": i, 'protocol': 'TCP'})
        container = {"name": container_name, "image": container_image, "ports": port_list}
        # add special info
        container_env = prompt('  ? Env of container[yes|no]: ')
        if str2list(container_env)[0] == 'yes':
            container_env_name = prompt('    ? Name of env: ', validator=validator_null)
            container_env_value = prompt('    ? Value of env: ', validator=validator_null)
            container_env_name_list = str2list(container_env_name)
            container_env_value_list = str2list(container_env_value)
            if len(container_env_name_list) != len(container_env_value_list):
                click.secho("! The name's number of container's env not equal to value's number, please try again.",
                            fg='red')
                click.Context.exit(0)
            container["env"] = []
            for j in range(len(container_env_name_list)):
                container["env"].append({"name": container_env_name_list[j], "value": container_env_value_list[j]})
        container_volume = prompt('  ? Volume of container[yes|no]: ')
        if str2list(container_volume)[0] == 'yes':
            container_volume_name = prompt('    ? Name of volume: ', validator=validator_null)
            container_volume_path = prompt('    ? Path of volume: ', validator=validator_null)
            container_volume_name_list = str2list(container_volume_name)
            container_volume_path_list = str2list(container_volume_path)
            if len(container_volume_name_list) != len(container_volume_path_list):
                click.secho("! The name's number of container's volume not equal to path's number, please try again.",
                            fg='red')
                click.Context.exit(0)
            container["volumeMounts"] = []
            for k in range(len(container_volume_name_list)):
                container["volumeMounts"].append(
                    {"name": container_volume_name_list[k], "mountPath": container_volume_path_list[k]})

            # add host volume
            type_completer = WordCompleter(
                ['DirectoryOrCreate', 'Directory', 'FileOrCreate', 'File', 'Socket', 'CharDevice', 'BlockDevice'])
            host_volume_type = prompt('    ? Type of volume on host: ', completer=type_completer,
                                      validator=validator_null)
            host_volume_name = container_volume_name_list
            host_volume_path = container_volume_path_list
            deploy["spec"]["template"]["spec"]["volumes"] = []
            for l in range(len(host_volume_name)):
                deploy["spec"]["template"]["spec"]["volumes"].append(
                    {"name": host_volume_name[l], "hostPath": {"path": host_volume_path, "type": host_volume_type}})
        deploy["spec"]["template"]["spec"]["containers"].append(container)

        # add restart
        restart = prompt(FormattedText([('#B58900', '? Restart policy[yes|no]: ')]), validator=validator_null)
        if restart == 'yes':
            deploy["spec"]["template"]["spec"]["restartPolicy"] = "Always"

        # begin generate yaml file
        click.secho('  Begin generate yaml file ......', fg='black', bg='green')
        yaml_file = yaml.dump_all(deploy)
        file_name = name + "_deploy.yaml"
        with open(file_name, 'w') as file:
            file.write(yaml_file)


def generate_service():
    pass


def generate_ingress():
    pass


if __name__ == '__main__':
    cli()
