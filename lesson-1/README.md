# Ansible. Lesson 1

- Что такое Ansible
- Установка Ansible
- Настройка инвентаря
- Выполнение ad-hoc команд
- Создание первого playbook

## Что такое Ansible

- `ansible` - выполнение ad-hoc команд на удаленных хостах
- `ansible-config` - управление конфигурацией Ansible
- `ansible-console` - интерактивная консоль Ansible
- `ansible-doc` - документация по модулям Ansible
- `ansible-galaxy` - управление ролями Ansible Galaxy
- `ansible-inventory` - работа с инвентарем Ansible
- `ansible-playbook` - выполнение playbook Ansible
- `ansible-pull` - выполнение playbook на удаленных хостах
- `ansible-vault` - шифрование и дешифрование файлов с помощью Ansible Vault

Ansible - это инструмент автоматизации, который позволяет управлять конфигурацией, развертыванием и оркестрацией приложений. Он использует декларативный подход, что позволяет описывать желаемое состояние системы, а Ansible сам позаботится о том, чтобы достичь этого состояния.

Распространенные варианты использования Ansible:

- Устранение повторений и упрощение рабочих процессов
- Управление и поддержание конфигурации системы
- Непрерывное развертывание сложного программного обеспечения
- Выполнение обновлений без простоев

Ansible использует простые, легко читаемые скрипты, называемые плейбуками, для автоматизации задач. В плейбуке вы объявляете желаемое состояние локальной или удаленной системы. Ansible обеспечивает, чтобы система оставалась в этом состоянии.

Ansible разработан на основе следующих принципов:

**Архитектура без агентов**
Низкие эксплуатационные расходы за счет отсутствия необходимости установки дополнительного ПО в ИТ-инфраструктуре.

**Простота**
Сценарии автоматизации используют понятный YAML-синтаксис для кода, который читается как документация. Ansible также децентрализован, использует SSH с существующими учетными данными ОС для доступа к удаленным машинам.

**Масштабируемость и гибкость**
Легко и быстро масштабируйте автоматизируемые системы благодаря модульной конструкции, поддерживающей широкий спектр операционных систем, облачных платформ и сетевых устройств.

**Идемпотентность и предсказуемость**
Когда система находится в состоянии, описанном в вашем playbook, Ansible ничего не меняет, даже если playbook запускается несколько раз.

## Установка Ansible

Если нет pip, то установим его:

```bash
sudo apt update
sudo apt install python3-pip y
```

Устанавливаем Ansible:

```bash
sudo apt install ansible -y
```

Создаем каталог для проекта:

```bash
mkdir ansible
cd ansible
```

Файл инвентаря по умолчанию находится в `/etc/ansible/hosts`, но мы создадим свой файл инвентаря в каталоге проекта.

Создаем файл `inventory.ini`:

```bash
nano inventory.ini
```

## Настройка инвентаря

Ansible использует инвентарь для определения хостов, на которых будут выполняться задачи. Файлы создаются в формате `ini` или `yaml`. Можно использовать как IP-адреса, так и имена (FQDN). Все хосты принадлежат группам:

- `all` - все хосты
- `ungrouped` - не принадлежат ни одной группе

- Имена групп осмысленные и уникальные. Имена групп чувствительны к регистру.
- Избегайте пробелов, дефисов и предшествующих цифр в начале имени группы. Можно _
- Группируйте хосты в своем инвентаре логически по их Что, Где и Когда.
  - **Что**
    Группируйте хосты в соответствии с топологией, например: db, web, leaf, spine.
  - **Где**
    Группируйте хосты по географическому положению, например: центр обработки данных, регион, этаж, здание.
  - **Когда**
    Группируйте хосты по этапам, например: разработка, тестирование, постановка, производство.

```ini
10.0.0.1 # Хост в группе all и ungrouped

[servers] # Название группы хостов
10.0.0.2 # Хост в группе servers
server3 ansible_host=10.0.0.3 # Хост в группе servers с алиасом
```

Можно использовать приращение:

```ini
[servers]
server[1:30]

# Получится:
server01
server02
# ...
server30
```

Можно использовать шаг:

```ini
server[1:30:2]
# Получится:
server01
server03
server05
# ...
server29

# Буквы
[databases]
db-[a:f].example.com
# Получится:
db-a.example.com
db-b.example.com
db-c.example.com
db-d.example.com
db-e.example.com
db-f.example.com
```

Делим на группы:

```ini
10.250.1.95

[web]
10.250.1.97

[test]
server3 ansible_host=10.250.1.96
```

Модификаторы групп:

- `:children` - Вложенные группы
- `:vars` - Переменные инвентаря

```ini
[web_servers:children]
web
test

[web_servers:vars]
ansible_user=user
```

Проверка инвентаря:

```bash
ansible-inventory -i inventory.ini --host server3 # вывод информации о хосте
ansible-inventory -i inventory.ini --graph # граф зависимостей групп и хостов
ansible-inventory -i inventory.ini --list # вывод информации о всех хостах
```

Конвертация инвентаря в YAML:

```bash
ansible-inventory -i inventory.ini -y --list > inventory.yaml
```

Пример на YAML:

```yaml
servers:
  hosts:
    srv1:
      ansible_host: 192.0.2.50
      ansible_user: user
    srv2:
      ansible_host: 192.0.2.51
    srv3:
      ansible_host: 192.0.2.52

web_servers:
  children:
    servers:
    group_name:
```

Игнорирование fingerprint SSH `ansible.cfg`:

```ini
[defaults]
host_key_checking = False
```

Создание SSH ключа и копирование его на удаленный хост:

```bash
ssh-keygen -t rsa -b 4096
ssh-copy-id vagrant@10.250.1.95
```

## Выполнение ad-hoc команд

Ansible позволяет выполнять команды на удаленных хостах без необходимости создания playbook. Это называется ad-hoc командами.

```bash
ansible -i inventory.ini servers -m ping # Пингует все хосты в группе servers
ansible -i inventory.yaml servers -m ping # Пингует все хосты в группе servers
ansible -i inventory.ini all -m command -a "useradd -m -g users user" -b # Ошибка если дважды. Желательно использовать модуль
ansible -i inventory.ini all -m user -a "name=user state=present" -b # Создает пользователя user
ansible -i inventory.ini all -m copy -a "src=test.txt dest=/home/test.txt" -b # Копирует файл test.txt на удаленные хосты
ansible -i inventory.ini all -m command -a "ls -l" # Выполняет команду ls -l на всех хостах
ansible -i inventory.ini servers -m apt -a "name=git state=present" -b # Устанавливает git на все хосты в группе servers
ansible -i inventory.yaml all -m reboot -b # Перезагружает все хосты
```

[All modules](https://docs.ansible.com/ansible/latest/collections/index_module.html)

## Создание первого playbook

Создадим playbook для установки и запуска nginx на удаленных серверах.
Playbook - это файл, в котором описаны задачи, которые Ansible должен выполнить на удаленных хостах. Playbook написан в формате YAML и состоит из одного или нескольких play.

Создаем файл `index.html` для копирования на удаленные хосты:

```html
Hello world!
```

Создаем файл `playbook.yaml`:

```yaml
- name: Install and start nginx
  hosts: servers
  become: true
  tasks:
    - name: Install nginx
      apt:
        update_cache: yes
        name: nginx
        state: latest # должно быть present

    - name: Copy index.html
      copy:
        src: index.html
        dest: /var/www/html/index.html
      notify: Restart nginx

    - name: Start nginx
      service:
        name: nginx
        enabled: on
        state: started

  handlers:
    - name: Restart nginx
      service:
        name: nginx
        state: restarted
```

Линтинг playbook: `ansible-lint` для проверки синтаксиса и стиля вашего playbook:

```bash
ansible-lint playbook.yaml
```

Запускаем чек мод. Режим проверки Ansible позволяет вам выполнить плейбук без внесения каких-либо изменений в ваши системы:

```bash
ansible-playbook -i inventory.ini playbook.yaml --check
```

Запускаем playbook:

```bash
ansible-playbook -i inventory.ini playbook.yaml -f 10

# Можно использовать несколько инвентарей. Выполнение в порядке указания
ansible-playbook get_logs.yml -i staging -i production
```

Проверяем статус:

```bash
ansible -i inventory.ini servers -m command -a "systemctl status nginx" -b
```

Можно указывать переменные в playbook:

```yaml
```yaml
- name: Install and start nginx
  hosts: servers
  become: true

  vars:
    source_file: index.html
    dest_file: /var/www/html/index.html

  tasks:
    - name: Install nginx
      apt:
        update_cache: yes
        name: nginx
        state: present

    - name: Copy file
      copy:
        src: {{ source_file }}
        dest: {{ dest_file }}

      notify: Restart nginx

    - name: Start nginx
      service:
        name: nginx
        enabled: on
        state: started

  handlers:
    - name: Restart nginx
      service:
        name: nginx
        state: restarted
```

## Вынос переменных в отдельный файл

Создаем каталог `group_vars` и файл с названием группы. Например, файл конфигурации:

```ini
[servers]
10.250.1.97

[test]
server3 ansible_host=10.250.1.96

# [servers:vars]
# ansible_user=user
```

`group_vars/servers.yaml`:

```yaml
ansible_user: user
ansible_password: password
```

Также можно создать каталог с именем группы в каталоге `group_vars`. Будут прочитаны все файлы в этом каталоге по алфавиту.

```yaml
a_group:
  vars:
    testvar: a
    ansible_group_priority: 10
b_group:
  vars:
    testvar: b
```
