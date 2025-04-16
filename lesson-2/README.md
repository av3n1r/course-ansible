# Ansible. Lesson 2

- Переменные в `ansible.cfg`
- Разделение инвентаря
- Переменные в playbook
- Ansible Vault

Серверы для лабораторной работы (адреса из `Vagrantfile`):

| Имя сервера | IP-адрес       | Дистрибутив       | Cерверная роль       | Группа      |
| ----------- | -------------- | ----------------- | -------------------- | ----------- |
| `server1`   | `10.250.1.165` | `fedora-latest`   | HAProxy              | haproxy     |
| `server2`   | `10.250.1.166` | `centos-stream-9` | MariaDB              | database    |
| `server3`   | `10.250.1.167` | `ubuntu-24.04`    | Nginx frontend-1     | frontend    |
| `server4`   | `10.250.1.170` | `debian-12`       | Nginx frontend-2     | frontend    |
| `server5`   | `10.250.1.169` | `oracle-9`        | Application          | application |
| `server7`   | `10.250.1.168` | `almalinux-9`     | Prometheus + Grafana | monitoring  |

- Ко всем серверам серверам доступ по ssh ключу
- Для `server5` доступ по паролю

## Переменные в `ansible.cfg`

Файл конфигурации Ansible `ansible.cfg` используется для настройки параметров Ansible. Он может находиться в нескольких местах, и Ansible будет искать его в следующем порядке:

- `ANSIBLE_CONFIG` (environment variable if set)
- `ansible.cfg` (in the current directory)
- `~/.ansible.cfg` (in the home directory)
- `/etc/ansible/ansible.cfg`

Используется первый найденный файл, остальные игнорируются.

Ansible не будет автоматически загружать файл конфигурации из текущего каталога, если каталог доступен для записи всем.

Пример файла конфигурации:

```ini
# some basic default values...
inventory = /etc/ansible/hosts  ; Путь к инвентарю
host_key_checking = False ; Отключение проверки ключа хоста (Fingerprint)
remote_user = vagrant ; Имя пользователя по умолчанию
private_key_file = ~/.ssh/id_rsa ; Путь к приватному ключу
```

Переменные окружения:

- `ANSIBLE_CONFIG` - позволяет переопределить путь к конфигурационному файлу Ansible
- `ANSIBLE_VAULT_PASSWORD_FILE` - указывает файл с паролем для Ansible Vault
- `ANSIBLE_ROLES_PATH` - пути для поиска ролей Ansible
- `ANSIBLE_HOST_KEY_CHECKING` - отключение проверки SSH ключей хостов
- `ANSIBLE_INVENTORY` - путь к файлу инвентаризации
- `ANSIBLE_REMOTE_USER` - пользователь для подключения к удаленным хостам
- `ANSIBLE_PRIVATE_KEY_FILE` - путь к приватному SSH ключу
- `ANSIBLE_FORKS` - количество параллельных процессов
- `ANSIBLE_RETRY_FILES_ENABLED` - включение/отключение файлов повторных попыток
- `ANSIBLE_LOG_PATH` - путь к файлу логов

Создание файла конфигурации:

```bash
ansible-config init --disabled > ansible.cfg
# or
ansible-config init --disabled -t all > ansible.cfg
```

Переменные окружения имеют приоритет над переменными в файле конфигурации. Параметры в командной строке имеют приоритет над ними.

- https://docs.ansible.com/ansible/latest/collections/environment_variables.html
- https://docs.ansible.com/ansible/latest/reference_appendices/config.html

Наиболее полезные и распространенные можно вывести в консоль командой `ansible-config`.

## Разделение инвентаря

Просмотр инвентаря:

```bash
ansible-inventory --list -i inventory -y
```

Инвентарь можно разделить на несколько файлов:

- `/etc/ansible/inventory/servers_1`
- `/etc/ansible/inventory/servers_2`

 Игнорируются файлы с расширениями `.orig`, `.ini`, `.cfg`, `.retry`.

При выполнении `ansible-playbook` можно указать несколько файлов инвентаря или каталог:

```bash
ansible-playbook -i inventory/servers_1 -i inventory/servers_2 playbook.yaml
ansible-playbook -i inventory playbook.yaml
```

При этом Ansible объединит все файлы в один и выполнит playbook.

## Переменные в инвентаре

В инвентаре можно создавать любые переменные, которые будут доступны в playbook и ролях. Например, можно использовать переменную `ansible_user`, которая будет использоваться для подключения к удаленным хостам или создать свою переменную `my_var`.

Переменные подключения к хостам: https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html#connecting-to-hosts-behavioral-inventory-parameters

Переменные можно назначить группе:

```ini
[group1]
server1
[group:vars]
my_var = 1
```

На YAML:

```yaml
group1
  hosts:
    server1:
      ansible_host:10.0.0.1
      var1: test
  vars:
    var2: test
```

В инвентаре переменные правильно хранить в каталогах `group_vars` и `host_vars`. Допускаются расширения `.yml`, `.yaml`, `.json`.

Поиск каталогов `group_vars` и `host_vars` происходит на том же уровне, что и файл инвентаря. Например, если файл инвентаря находится в `/etc/ansible/inventory`, то Ansible будет искать переменные в следующих каталогах:

- `/etc/ansible/group_vars/haproxy.txt`
- `/etc/ansible/group_vars/database.yaml`
- `/etc/ansible/group_vars/frontend`
- ...

- `/etc/ansible/host_vars/server1`
- `/etc/ansible/host_vars/server2`
- `/etc/ansible/host_vars/server3`
- ...

Можно использовать каталоги с аналогичным именем:

- `/etc/ansible/group_vars/haproxy/vars1`
- `/etc/ansible/group_vars/haproxy/vars2`

Переменные записываются в `YAML` формате.

Пример файла с переменными `group_vars/frontend`:

```yaml
ansible_user: vagrant
ansible_password: vagrant
```

Приоритет переменных (от меньшего к большему):

- all group (потому что это родительская группа)
- parent group
- child group
- host

## Переменные в playbook

Переменные в playbook можно задавать в секции `vars`,

```yaml
- name: Copy file
  hosts: all

  vars:
    source: ./index.html
    destination: /var/www/html/index.html

  tasks:
    - name: Copy file
      copy:
        src: {{ source }}
        dest: {{ destination }}
```

Переменные можно использовать из переменных инвентаря:

`host_vars/server1`:

```yaml
source: ./index.html
destination: /var/www/html/index.html
```

```yaml
- name: Copy file
  hosts: all

  tasks:
    - name: Copy file
      copy:
        src: {{ source }}
        dest: {{ destination }}
```

Переменные можно указывать при запуске playbook с помощью `-extra-vars` или `-e` (наивысший приоритет):

```bash
ansible-playbook -i inventory -e "var1=./index.html destination=/var/www/html/index.html" playbook.yaml
```

Переменные можно выводить в консоль в процессе выполнения playbook:

```yaml
- name: Copy file
  hosts: all

  tasks:
    - debug:
        msg: "Source: {{ source }}, Destination: {{ destination }}"

    - debug:
        var: source
        verbosity: 2
```

Переменные можно создавать в playbook с помощью `set_fact`:

`host_vars/server1`:

```yaml
owner: Aleksey
group: frontend
```

```yaml
- name: Hello
  hosts: all

  vars:
    var1: "Hello"

  tasks:
    - set_fact:
        var: var2
        value: "{{ var1 }} {{ owner}} from {{ group }} group"

    - debug:
        msg: {{ var2 }}
```

Можно использовать переменные из `ansible -m setup`:

```yaml
- name: Get facts
  hosts: all

  tasks:
    - debug:
        msg: "{{ ansible_os_family }}, {{ ansible_pkg_mgr }}, {{ ansible_all_ipv4_addresses[0] }}"

    - debug:
        msg: "OS: {{ ansible_distribution }} {{ ansible_distribution_version }}, Kernel: {{ ansible_kernel }}, CPU: {{ ansible_processor_cores }} cores, RAM: {{ ansible_memtotal_mb }} MB"
```

Вывод результата команды:

```yaml
- name: Get memory
  hosts: all

  tasks:
    - shell: free -h
      register: result

    - debug:
        var: result.stdout_lines
```

В playbook можно вставлять другие таски и плейбуки. При этом переменные будут доступны в импортируемом playbook (в отличие от `include`):

```yaml
- name: Import playbook
  hosts: all

  tasks:
    - name: Import tasks
      import_tasks: tasks.yaml

- name: Import playbook
  import_playbook: playbook.yaml
```

### Ansible Vault

Ansible Vault позволяет шифровать и дешифровать файлы. Использовать зашифрованные данные можно для ad-hoc и playbook команд предоставляя пароль в командной строке или используя файл с паролем. В `ansible.cfg` можно указать путь к файлу с паролем, чтобы не указывать его каждый раз в командной строке.

Действия выполняются с помощью команды `ansible-vault`.

Создание шифрованного файла:

```bash
ansible-vault create secret.yaml
```

Просмотр шифрованного файла:

```bash
ansible-vault view secret.yaml
```

Редактирование шифрованного файла:

```bash
ansible-vault edit secret.yaml
```

Смена пароля:

```bash
ansible-vault rekey secret.yaml
```

Шифрование файла:

```bash
ansible-vault encrypt secret.yaml
```

Дешифрование файла:

```bash
ansible-vault decrypt secret.yaml
```

Шифрование строки:

```bash
ansible-vault encrypt_string 'my_secret' --name 'my_secret'
```

Для запуска шифрованного playbook нужно указать пароль в командной строке:

```bash
ansible-playbook -i inventory playbook.yaml --ask-vault-pass
```

или указать файл с паролем:

```bash
ansible-playbook -i inventory playbook.yaml --vault-password-file ~/.ansible_vault_pass
```

или указать переменную окружения:

```bash
export ANSIBLE_VAULT_PASSWORD_FILE=~/.ansible_vault_pass
```

Использование меток.

- Создаем два файла с разными паролями `file_pass1` = `password1` и `file_pass2` = `password2`.
- Шифруем разные переменные в одном файле:
  - `ansible-vault encrypt_string 'my_secret1' --name 'my_secret1' --vault-id pass1@file_pass1`
  - `ansible-vault encrypt_string 'my_secret2' --name 'my_secret2' --vault-id pass2@file_pass2`
- Запускаем playbook с указанием обоих файлов с паролями:
  - `ansible-playbook -i inventory playbook.yaml --vault-id pass1@file_pass1 --vault-id pass2@file_pass2`

Примеры использования:

- `ansible-playbook --vault-id dev@file_pass1 --vault-id prod@file_pass2 site.yml`
- `ansible-playbook --vault-id my-vault-password-client.py`
