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
    click.echo('')
    click.secho('  Begin ' + kind + ' workflow ......', fg='black', bg='green')
    if kind == 'deployment':
        generate_deploy()
    elif kind == 'service':
        generate_service()
    else:
        generate_ingress()


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
                    {"name": host_volume_name[l], "hostPath": {"path": host_volume_path[l], "type": host_volume_type}})
        deploy["spec"]["template"]["spec"]["containers"].append(container)

        # add restart
        restart = prompt(FormattedText([('#B58900', '? Restart policy[yes|no]: ')]), validator=validator_null)
        if restart == 'yes':
            deploy["spec"]["template"]["spec"]["restartPolicy"] = "Always"

        # begin generate yaml file
        click.secho('  Begin generate yaml file ......', fg='black', bg='green')
        yaml_file = yaml.dump(deploy, default_flow_style=False)
        file_name = name + "_deploy.yaml"
        with open(file_name, 'w') as file:
            file.write(yaml_file)
        click.secho('  Generate yaml file success!', fg='black', bg='green')
        click.echo('')
        click.secho('  You can copy yaml to remote host: ', fg='blue')
        click.secho('    scp ' + file_name + ' remote_ip:' + file_name, fg='green')
        click.secho('  And create deployment: ', fg='blue')
        click.secho('    kubectl create -f ' + file_name, fg='green')
        click.echo('')


def generate_service():
    """
    Generate service yaml file, need follow parameters:
        - service name
        - service labels
        - service port
        - deployment labels
    """

    # service template
    service = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {},
        "spec": {"ports": [], "selector": {}}
    }

    # add name
    name = prompt(FormattedText([('#B58900', '? Please enter the name of service: ')]), validator=validator_null)
    service["metadata"]["name"] = name

    # add labels
    service_labels = prompt('? Labels of service[yes|no]: ')
    if str2list(service_labels)[0] == 'yes':
        service_labels_key = prompt("  ? Name of labels: ", validator=validator_null)
        service_labels_value = prompt('  ? Value of labels: ', validator=validator_null)
        if len(str2list(service_labels_key)) != len(str2list(service_labels_value)):
            click.secho("! The key's number of labels not equal to value's number, please try again.", fg='red')
            click.Context.exit(0)
        service["metadata"]["labels"] = dict(zip(str2list(service_labels_key), str2list(service_labels_value)))

    # add ports
    click.secho('? Please enter the port information (if more than one, use space): ', fg='yellow')
    service_port = prompt('  ? Port of service: ', validator=validator_null)
    container_port = prompt('  ? Port of container: ', validator=validator_null)
    service_port_list = str2list(service_port)
    container_port_list = str2list(container_port)
    if len(service_port_list) != len(container_port_list):
        click.secho("! The port's number of service not equal to container, please try again.",
                    fg='red')
        click.Context.exit(0)
    # check port type
    service_port_list_int = None
    container_port_list_int = None
    try:
        service_port_list_int = list(map(int, service_port_list))
        container_port_list_int = list(map(int, container_port_list))
    except:
        click.secho("! The type of port is not int, please try again.", fg='red')
        click.Context.exit(0)
    for i in range(len(service_port_list)):
        service["spec"]["ports"].append({"port": service_port_list_int[i], "targetPort": container_port_list_int[i],
                                         "protocol": "TCP", "name": "http"})

    # add deployment labels
    click.secho('? Please enter the labels information of deployment (if more than one, use space): ', fg='yellow')
    labels_key = prompt("  ? Name of labels: ", validator=validator_null)
    labels_value = prompt('  ? Value of labels: ', validator=validator_null)
    if len(str2list(labels_key)) != len(str2list(labels_value)):
        click.secho("! The key's number of labels not equal to value's number, please try again.", fg='red')
        click.Context.exit(0)
    service["spec"]["selector"] = dict(zip(str2list(labels_key), str2list(labels_value)))

    # begin generate yaml file
    click.secho('  Begin generate yaml file ......', fg='black', bg='green')
    yaml_file = yaml.dump(service, default_flow_style=False)
    file_name = name + "_service.yaml"
    with open(file_name, 'w') as file:
        file.write(yaml_file)
    click.secho('  Generate yaml file success!', fg='black', bg='green')
    click.echo('')
    click.secho('  You can copy yaml to remote host: ', fg='blue')
    click.secho('    scp ' + file_name + ' remote_ip:' + file_name, fg='green')
    click.secho('  And create service: ', fg='blue')
    click.secho('    kubectl create -f ' + file_name, fg='green')
    click.echo('')


def generate_ingress():
    """
    Generate ingress yaml file, need follow parameters:
        - ingress name
        - rules
            - host name
            - path
            - service name
            - service port
    """

    # ingress template
    ingress = {
        "apiVersion": "extensions/v1beta1",
        "kind": "Ingress",
        "metadata": {'annotations': {'kubernetes.io/ingress.class': 'nginx',
                                     'nginx.ingress.kubernetes.io/ssl-redirect': 'false'}},
        "spec": {"rules": []}
    }

    # add name
    name = prompt(FormattedText([('#B58900', '? Please enter the name of ingress: ')]), validator=validator_null)
    ingress["metadata"]["name"] = name

    # add rules
    click.secho('? Please enter the rules information: ', fg='yellow')
    rule_host = prompt('  ? Host of rule (if more than one, use space): ', validator=validator_null)
    rule_host_list = str2list(rule_host)
    for rule in rule_host_list:
        click.secho('    Begin ' + str(rule_host_list.index(rule) + 1) + 'th rule: ', fg='magenta')
        rule_path = prompt('    ? Path of rule (if more than one, use space): ', validator=validator_null)
        rule_path_list = str2list(rule_path)
        paths = []
        for path in rule_path_list:
            click.secho('      Begin ' + str(rule_path_list.index(path) + 1) + 'th path: ', fg='magenta')
            rule_service_name = prompt('      ? Service name: ', validator=validator_null)
            rule_service_port = prompt('      ? Service port: ', validator=validator_digit)
            paths.append(
                {"path": path, "backend": {"serviceName": rule_service_name, "servicePort": int(rule_service_port)}})
        ingress["spec"]["rules"].append({"host": rule, "http": {"paths": paths}})

    # begin generate yaml file
    click.secho('  Begin generate yaml file ......', fg='black', bg='green')
    yaml_file = yaml.dump(ingress, default_flow_style=False)
    file_name = name + "_ingress.yaml"
    with open(file_name, 'w') as file:
        file.write(yaml_file)
    click.secho('  Generate yaml file success!', fg='black', bg='green')
    click.echo('')
    click.secho('  You can copy yaml to remote host: ', fg='blue')
    click.secho('    scp ' + file_name + ' remote_ip:' + file_name, fg='green')
    click.secho('  And create ingress: ', fg='blue')
    click.secho('    kubectl create -f ' + file_name, fg='green')
    click.echo('')
