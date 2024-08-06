# command-instead-of-shell

This rule identifies uses of `shell` modules instead of a `command` one when
this is not really needed. Shell is considerably slower than command and should
be avoided unless there is a special need for using shell features, like
environment variable expansion or chaining multiple commands using pipes.

## Problematic Code

```yaml
---
- name: Problematic example
  hosts: localhost
  tasks:
    - name: Echo a message
      ansible.builtin.shell: echo hello # <-- command is better in this case
      changed_when: false
```

## Correct Code

```yaml
---
- name: Correct example
  hosts: localhost
  tasks:
    - name: Echo a message
      ansible.builtin.command: echo hello
      changed_when: false
```

# deprecated-local-action

This rule recommends using `delegate_to: localhost` instead of the
`local_action`.

## Problematic Code

```yaml
---
- name: Task example
  local_action: # <-- this is deprecated
    module: ansible.builtin.debug
```

## Correct Code

```yaml
- name: Task example
    ansible.builtin.debug:
  delegate_to: localhost # <-- recommended way to run on localhost
```

# jinja

This rule can report problems related to jinja2 string templates. The current
version can report:

- `jinja` when there are no spaces between variables
  and operators, including filters, like `{{ var_name | filter }}`. This
  improves readability and makes it less likely to introduce typos.
- `jinja` when the jinja2 template is invalid, like `{{ {{ '1' }} }}`,
  which would result in a runtime error if you try to use it with Ansible, even
  if it does pass the Ansible syntax check.

As jinja2 syntax is closely following Python one we aim to follow
(https://black.readthedocs.io/en/stable/) formatting rules. If you are
curious how black would reformat a small snippet feel free to visit
(https://black.vercel.app/) site. Keep in mind to not
include the entire jinja2 template, so instead of `{{ 1+2==3 }}`, do paste
only `1+2==3`.

In ansible, `changed_when`, `failed_when`, `until`, `when` are considered to
use implicit jinja2 templating, meaning that they do not require `{{ }}`. Our
rule will suggest the removal of the braces for these fields.

## Problematic code

```yaml
---
- name: Some task
  vars:
    foo: "{{some|dict2items}}" # <-- jinja
    bar: "{{ & }}" # <-- jinja
  when: "{{ foo | bool }}" # <-- jinja - 'when' has implicit templating
```

## Correct code

```yaml
---
- name: Some task
  vars:
    foo: "{{ some | dict2items }}"
    bar: "{{ '&' }}"
  when: foo | bool
```

## Current limitations

In its current form, this rule presents the following limitations:

- Jinja2 blocks that have newlines in them will not be reformatted because we
  consider that the user deliberately wanted to format them in a particular way.
- Jinja2 blocks that use tilde as a binary operation are ignored because black
  does not support tilde as a binary operator. Example: `{{ a ~ b }}`.
- Jinja2 blocks that use dot notation with numbers are ignored because python
  and black do not allow it. Example: `{{ foo.0.bar }}`

# key-order

This rule recommends reordering key names in ansible content to make
code easier to maintain and less prone to errors.

Here are some examples of common ordering checks done for tasks and handlers:

- `name` must always be the first key for plays, tasks and handlers
- on tasks, the `block`, `rescue` and `always` keys must be the last keys,
  as this would avoid accidental miss-indentation errors between the last task
  and the parent level.

## Problematic code

```yaml
---
- hosts: localhost
  name: This is a playbook # <-- name key should be the first one
  tasks:
    - name: A block
      block:
        - name: Display a message
          debug:
            msg: "Hello world!"
      when: true # <-- when key should be before block
```

## Correct code

```yaml
---
- name: This is a playbook
  hosts: localhost
  tasks:
    - name: A block
      when: true
      block:
        - name: Display a message
          debug:
            msg: "Hello world!"
```

## Reasoning

Making decisions about the optimal order of keys for ansible tasks or plays is
no easy task, as we had a huge number of combinations to consider. This is also
the reason why we started with a minimal sorting rule (name to be the first),
and aimed to gradually add more fields later, and only when we find the proofs
that one approach is likely better than the other.

### Why I no longer can put `when` after a `block`?

Try to remember that in real life, `block/rescue/always` have the habit to
grow due to the number of tasks they host inside, making them exceed what a single screen. This would move the `when` task further away from the rest of the task properties. A `when` from the last task inside the block can
easily be confused as being at the block level, or the reverse. When tasks are
moved from one location to another, there is a real risk of moving the block
level when with it.

By putting the `when` before the `block`, we avoid that kind of risk. The same risk applies to any simple property at the task level, so that is why
we concluded that the block keys must be the last ones.

Another common practice was to put `tags` as the last property. Still, for the
same reasons, we decided that they should not be put after block keys either.

# name

This rule identifies several problems related to the naming of tasks and plays.
This is important because these names are the primary way to **identify** and
**document** executed operations on the console, logs or web interface.

This rule can produce messages as:

- `name` - All names should start with an uppercase letter for languages
  that support it.
- `name` - All tasks should be named.
- `name` - All plays should be named.
- `name` - Prefix task names in sub-tasks files. (opt-in)
- `name` - Jinja templates should only be at the end of 'name'. This
  helps with the identification of tasks inside the source code when they fail.
  The use of templating inside `name` keys is discouraged as there are multiple
  cases where the rendering of the name template is not possible.

If you want to ignore some of the messages above, you can add any of them to the
`skip_list`.

## name

This rule applies only to included task files that are not named `main.yml`. It
suggests adding the stem of the file as a prefix to the task name.

For example, if you have a task named `Restart server` inside a file named
`tasks/deploy.yml`, this rule suggests renaming it to `deploy | Restart server`,
so it would be easier to identify where it comes from.

For the moment, this sub-rule is just an **opt-in**, so you need to add it to
your `enable_list` to activate it.

!!! note

    This rule was designed by [Red Hat Community of Practice](https://redhat-cop.github.io/automation-good-practices/#_prefix_task_names_in_sub_tasks_files_of_roles). The reasoning behind it being
    that in a complex roles or playbooks with multiple (sub-)tasks file, it becomes
    difficult to understand which task belongs to which file. Adding a prefix, in
    combination with the role’s name automatically added by Ansible, makes it a
    lot easier to follow and troubleshoot a role play.

## Problematic code

```yaml
---
- hosts: localhost # <-- playbook name
  tasks:
    - name: create placefolder file # <-- name due lack of capital letter
      ansible.builtin.command: touch /tmp/.placeholder
```

## Correct code

```yaml
---
- name: Play for creating placeholder
  hosts: localhost
  tasks:
    - name: Create placeholder file
      ansible.builtin.command: touch /tmp/.placeholder
```

# no-free-form

This rule identifies any use of
(https://docs.ansible.com/ansible/2.7/user_guide/playbooks_intro.html#action-shorthand)
module calling syntax and asks for switching to the full syntax.

**Free-form** syntax, also known as **inline** or **shorthand**, can produce
subtle bugs. It can also prevent editors and IDEs from providing feedback,
autocomplete and validation for the edited line.

!!! note

    As long you just pass a YAML string that contains a `=` character inside as the
    parameter to the action module name, we consider this as using free-form syntax.
    Be sure you pass a dictionary to the module, so the free-form parsing is never
    triggered.

As `raw` module only accepts free-form, we trigger `no-free-form` only if
we detect the presence of `executable=` inside raw calls. We advise the explicit
use of `args:` for configuring the executable to be run.

This rule can produce messages as:

- `no-free-form` - Free-form syntax is discouraged.
- `no-free-form` - Passing a non-string value to `raw` module is
  neither documented nor supported.

## Problematic code

```yaml
---
- name: Example with discouraged free-form syntax
  hosts: localhost
  tasks:
    - name: Create a placefolder file
      ansible.builtin.command: chdir=/tmp touch foo # <-- don't use free-form
    - name: Use raw to echo
      ansible.builtin.raw: executable=/bin/bash echo foo # <-- don't use executable=
      changed_when: false
```

## Correct code

```yaml
---
- name: Example that avoids free-form syntax
  hosts: localhost
  tasks:
    - name: Create a placefolder file
      ansible.builtin.command:
        cmd: touch foo # <-- ansible will not touch it
        chdir: /tmp
    - name: Use raw to echo
      ansible.builtin.raw: echo foo
      args:
        executable: /bin/bash # <-- explicit is better
      changed_when: false
```

# no-jinja-when

This rule checks conditional statements for Jinja expressions in curly brackets `{{ }}`.
Ansible processes conditionals statements that use the `when`, `failed_when`, and `changed_when` clauses as Jinja expressions.

An Ansible rule is to always use `{{ }}` except with `when` keys.
Using `{{ }}` in conditionals creates a nested expression, which is an Ansible
anti-pattern and does not produce expected results.

## Problematic Code

```yaml
---
- name: Example playbook
  hosts: localhost
  tasks:
    - name: Shut down Debian systems
      ansible.builtin.command: /sbin/shutdown -t now
      when: "{{ ansible_facts['os_family'] == 'Debian' }}" # <- Nests a Jinja expression in a conditional statement.
```

## Correct Code

```yaml
---
- name: Example playbook
  hosts: localhost
  tasks:
    - name: Shut down Debian systems
      ansible.builtin.command: /sbin/shutdown -t now
      when: ansible_facts['os_family'] == "Debian" # <- Uses facts in a conditional statement.
```

# no-log-password

This rule ensures playbooks do not write passwords to logs when using loops.
Always set the `no_log: true` attribute to protect sensitive data.

While most Ansible modules mask sensitive data, using secrets inside a loop can result in those secrets being logged.
Explicitly adding `no_log: true` prevents accidentally exposing secrets.

## Problematic Code

```yaml
---
- name: Example playbook
  hosts: localhost
  tasks:
    - name: Log user passwords
      ansible.builtin.user:
        name: john_doe
        comment: John Doe
        uid: 1040
        group: admin
        password: "{{ item }}"
      with_items:
        - wow
      no_log: false # <- Sets the no_log attribute to false.
```

## Correct Code

```yaml
---
- name: Example playbook
  hosts: localhost
  tasks:
    - name: Do not log user passwords
      ansible.builtin.user:
        name: john_doe
        comment: John Doe
        uid: 1040
        group: admin
        password: "{{ item }}"
      with_items:
        - wow
      no_log: true # <- Sets the no_log attribute to a non-false value.
```

# partial-become

This rule checks that privilege escalation is activated when changing users.

To perform an action as a different user with the `become_user` directive, you
must set `become: true`.

This rule can produce the following messages:

- `partial-become`: become_user requires become to work as expected, at
  play level.
- `partial-become`: become_user requires become to work as expected, at
  task level.

!!! warning

    While Ansible inherits have of `become` and `become_user` from upper levels,
    like play level or command line, we do not look at these values. This rule
    requires you to be explicit and always define both in the same place, mainly
    in order to prevent accidents when some tasks are moved from one location to
    another one.

## Problematic Code

```yaml
---
- name: Example playbook
  hosts: localhost
  become: true # <- Activates privilege escalation.
  tasks:
    - name: Start the httpd service as the apache user
      ansible.builtin.service:
        name: httpd
        state: started
      become_user: apache # <- Does not change the user because "become: true" is not set.
```

## Correct Code

```yaml
- name: Example playbook
  hosts: localhost
  tasks:
    - name: Start the httpd service as the apache user
      ansible.builtin.service:
        name: httpd
        state: started
      become: true # <- Activates privilege escalation.
      become_user: apache # <- Changes the user with the desired privileges.

# Stand alone playbook alternative, applies to all tasks

- name: Example playbook
  hosts: localhost
  become: true # <- Activates privilege escalation.
  become_user: apache # <- Changes the user with the desired privileges.
  tasks:
    - name: Start the httpd service as the apache user
      ansible.builtin.service:
        name: httpd
        state: started
```

## Problematic Code

```yaml
---
- name: Example playbook 1
  hosts: localhost
  become: true # <- Activates privilege escalation.
  tasks:
    - name: Include a task file
      ansible.builtin.include_tasks: tasks.yml
```

```yaml
---
- name: Example playbook 2
  hosts: localhost
  tasks:
    - name: Include a task file
      ansible.builtin.include_tasks: tasks.yml
```

```yaml
# tasks.yml
- name: Start the httpd service as the apache user
  ansible.builtin.service:
    name: httpd
    state: started
  become_user: apache # <- Does not change the user because "become: true" is not set.
```

## Correct Code

```yaml
---
- name: Example playbook 1
  hosts: localhost
  tasks:
    - name: Include a task file
      ansible.builtin.include_tasks: tasks.yml
```

```yaml
---
- name: Example playbook 2
  hosts: localhost
  tasks:
    - name: Include a task file
      ansible.builtin.include_tasks: tasks.yml
```

```yaml
# tasks.yml
- name: Start the httpd service as the apache user
  ansible.builtin.service:
    name: httpd
    state: started
  become: true # <- Activates privilege escalation.
  become_user: apache # <- Does not change the user because "become: true" is not set.
```

# yaml

This rule checks YAML syntax by using [yamllint] library but with a
[specific default configuration](#yamllint-configuration), one that is
compatible with both, our internal reformatter (`--fix`) and also [prettier].

You can disable YAML syntax violations by adding `yaml` to the `skip_list` in
your Ansible-lint configuration as follows:

```yaml
skip_list:
  - yaml
```

For more fine-grained control, disable violations for specific rules using tag
identifiers in the `yaml[yamllint_rule]` format as follows:

```yaml
skip_list:
  - yaml[trailing-spaces]
  - yaml[indentation]
```

If you want Ansible-lint to report YAML syntax violations as warnings, and not
fatal errors, add tag identifiers to the `warn_list` in your configuration, for
example:

```yaml
warn_list:
  - yaml[document-start]
```

!!! warning

    You cannot use `tags: [skip_ansible_lint]` to disable this rule but you can
    use [yamllint magic comments](https://yamllint.readthedocs.io/en/stable/disable_with_comments.html#disabling-checks-for-all-or-part-of-the-file) for tuning it.

See the
[list of yamllint rules](https://yamllint.readthedocs.io/en/stable/rules.html)
for more information.

Some of the detailed error codes that you might see are:

- `yaml[brackets]` - _too few spaces inside empty brackets_, or _too many spaces
  inside brackets_
- `yaml[colons]` - _too many spaces before colon_, or _too many spaces after
  colon_
- `yaml[commas]` - _too many spaces before comma_, or _too few spaces after
  comma_
- `yaml[comments-indentation]` - _Comment not indented like content_
- `yaml[comments]` - _Too few spaces before comment_, or _Missing starting space
  in comment_
- `yaml[document-start]` - _missing document start "---"_ or _found forbidden
  document start "---"_
- `yaml[empty-lines]` - _too many blank lines (...> ...)_
- `yaml[indentation]` - _Wrong indentation: expected ... but found ..._
- `yaml[key-duplicates]` - _Duplication of key "..." in mapping_
- `yaml[line-length]` - _Line too long (... > ... characters)_
- `yaml[new-line-at-end-of-file]` - _No new line character at the end of file_
- `yaml[octal-values]`: forbidden implicit or explicit [octal](#octals) value
- `yaml[syntax]` - YAML syntax is broken
- `yaml[trailing-spaces]` - Spaces are found at the end of lines
- `yaml[truthy]` - _Truthy value should be one of ..._

## Octals

As [YAML specification] regarding octal values changed at least 3 times in
[1.1], [1.2.0] and [1.2.2] we now require users to always add quotes around
octal values, so the YAML loaders will all load them as strings, providing a
consistent behavior. This is also safer as JSON does not support octal values
either.

By default, yamllint does not check for octals but our custom default ruleset
for it does check these. If for some reason, you do not want to follow our
defaults, you can create a `.yamllint` file in your project and this will take
precedence over our defaults.

## Additional Information for Multiline Strings

Adhering to yaml[line-length] rule, for writing multiline strings we recommend
using Block Style Indicator: literal style indicated by a pipe (|) or folded
style indicated by a right angle bracket (>), instead of escaping the newlines
with backslashes. Reference [guide] for writing multiple line strings in yaml.

## Problematic code

```yaml
# Missing YAML document start.
foo: 0777 # <-- yaml[octal-values]
foo2: 0o777 # <-- yaml[octal-values]
foo2: ... # <-- yaml[key-duplicates]
bar: ...       # <-- yaml[comments-indentation]
```

## Correct code

```yaml
---
foo: "0777" # <-- Explicitly quoting octal is less risky.
foo2: "0o777" # <-- Explicitly quoting octal is less risky.
bar: ... # Correct comment indentation.
```
