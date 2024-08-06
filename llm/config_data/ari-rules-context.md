
# W001
This rule checks a module name of a task in a generated playbook, and takes care of replacing short
name with module fully qualified collection name.

## Problematic Code
```yaml
---
- name: AWS Cloud operations
  hosts: localhost
  connection: local
  tasks:
    - name: Create a cloud instance
      ec2_instance: # should use FQCN
        state: running
        name: k8s_master
        region: us-east-1
        security_group: default
        instance_type: t2.micro
        image_id: ami-08e0ca9924195beba
        key_name: mykey
```

## Correct Code

```yaml
---
- name: AWS Cloud operations
  hosts: localhost
  connection: local
  tasks:
    - name: Create a cloud instance
      amazon.aws.ec2_instance: # updated with correct FQCN
        state: running
        name: k8s_master
        region: us-east-1
        security_group: default
        instance_type: t2.micro
        image_id: ami-08e0ca9924195beba
        key_name: mykey
```

# W013

This config rule use recommended boolean expressions (true / false)

## Problematic Code
```yaml
---
- name: Update web servers
  hosts: webservers
  remote_user: root

  tasks:
    - name: Ensure apache is at the latest version
      ansible.builtin.yum:
        name: "{{ name }}"
        skip_broken: "YES"  # boolean value should be "true"/"false"
```

## Correct Code

```yaml
---
- name: Update web servers
  hosts: webservers
  remote_user: root

  tasks:
    - name: Ensure apache is at the latest version
      ansible.builtin.yum:
        name: "{{ name }}"
        skip_broken: true  # replaced "yes" with "true"
```

# W016

This config rule avoid loop style if module option accepts list

## Problematic Code
```yaml
---
- name: Playbook example
  gather_facts: false
  become: false
  hosts: all
  tasks:
    - name: Install python and go
      ansible.builtin.package:  # check for module that can accepts list as parameter value
        name: "{{ item }}"
        state: present
      with_items:
        - python
        - go
```

## Correct Code

```yaml
---
- name: Playbook example
  gather_facts: false
  become: false
  hosts: all
  tasks:
    - name: Install python and go
      ansible.builtin.package: # removed loop style to use module in-built capability to accept list as parameter
        name:
          - python
          - go
        state: present
```

# W017

This config rule avoid empty string compare

## Problematic Code
```yaml
---
- name: Example playbook
  hosts: all
  tasks:
    - name: Shut down
      ansible.builtin.command: /sbin/shutdown -t now
      when: ansible_os_family == ""
```

## Correct Code

```yaml
---
- name: Update web servers
  hosts: webservers
  remote_user: root

  tasks:
    - name: Shut down
      ansible.builtin.command: /sbin/shutdown -t now
      when: "ansible_os_family | length == 0"
```


# W027

This config rule removes keys in suggestions if they are already defined in module_defaults

## Problematic Code
```yaml
---
- name: Deploy WordPress on AWS EC2
  hosts: localhost
  module_defaults:
    group/aws:
      aws_access_key: '{{ aws_access_key }}'
      aws_secret_key: '{{ aws_secret_key }}'
      region: us-east-1
  tasks:
    - name: Create vpc named wordpress
      amazon.aws.ec2_vpc_net:
        name: "wordpress"
        cidr_block: "{{ cidr_block }}"
        # region is defined in module_defaults; should be removed by W027
        region: us-east-1
      register: vpc
```

## Correct Code

```yaml
---
- name: Update web servers
  hosts: webservers
  remote_user: root
  tasks:
    - name: Create vpc named wordpress
      amazon.aws.ec2_vpc_net:
        name: "wordpress"
        cidr_block: "{{ cidr_block }}"
          # region is defined in module_defaults; should be removed by W027
        register: vpc
```
