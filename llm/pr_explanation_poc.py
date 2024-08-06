from langchain_community.document_loaders import TextLoader
import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_community.document_loaders.markdown import UnstructuredMarkdownLoader
from langchain.chains import create_retrieval_chain


def pr_explanation():
    # model = Ollama(model="mistral")
    model = Ollama(model="instructlab/granite-7b-lab")

    loader = UnstructuredMarkdownLoader("llm/rules.md", mode="elements", strategy="fast",) 
    documents = loader.load()
    # Define the embedding model
    embeddings=OllamaEmbeddings(model='nomic-embed-text')
    # Create the vector store
    vector = FAISS.from_documents(documents, embeddings)
    # Define a retriever interface
    retriever = vector.as_retriever()
    # Define prompt template
    prompt = ChatPromptTemplate.from_template("""You are an Ansible Expert. Please provide a summary of the changes in numbered bullet points, done by Ansible code bot, and how they improve the Ansible content, based on the ansible-lint rules.

    <context>
    {context}
    </context>

    Question: {input}""")

    # Create a retrieval chain to answer questions
    document_chain = create_stuff_documents_chain(model, prompt)
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    response = retrieval_chain.invoke({"input": """diff --git a/roles/run/tasks/health_checks/junos.yaml b/roles/run/tasks/health_checks/junos.yaml
index bacc328..bf80e6c 100644
--- a/roles/run/tasks/health_checks/junos.yaml
+++ b/roles/run/tasks/health_checks/junos.yaml
@@ -8,5 +8,5 @@


 - name: Show Summary facts
-  debug:
+  ansible.builtin.debug:
     msg: "{{ bgp_health }}"
diff --git a/roles/run/tasks/health_checks/vyos.yaml b/roles/run/tasks/health_checks/vyos.yaml
index b43708c..b71a087 100644
--- a/roles/run/tasks/health_checks/vyos.yaml
+++ b/roles/run/tasks/health_checks/vyos.yaml
@@ -1,6 +1,6 @@
 ---
 - name: Parse bgp summary
-  cli_parse:
+  ansible.utils.cli_parse:
     command: "show ip bgp summary"
     parser:
       name: ansible.netcommon.content_templates
diff --git a/roles/run/tasks/includes/configure.yaml b/roles/run/tasks/includes/configure.yaml
index 7916b41..8996f45 100644
--- a/roles/run/tasks/includes/configure.yaml
+++ b/roles/run/tasks/includes/configure.yaml
@@ -1,6 +1,6 @@
 ---
 - name: Invoke configure function
-  include_role:
-    name: network.base.resource_manager
   vars:
-    operation: 'configure'
+    operation: configure
+  ansible.builtin.include_role:
+    name: network.base.resource_manager
diff --git a/roles/run/tasks/includes/gather.yaml b/roles/run/tasks/includes/gather.yaml
index cdc447a..62ef559 100644
--- a/roles/run/tasks/includes/gather.yaml
+++ b/roles/run/tasks/includes/gather.yaml
@@ -3,8 +3,8 @@
   ansible.builtin.include_tasks: includes/resources.yaml

 - name: Invoke gather function
-  include_role:
-    name: network.base.resource_manager
   vars:
-    operation: 'gather'
-    resources: "{{ bgp_resources }}"
+    operation: gather
+    resources: '{{ bgp_resources }}'
+  ansible.builtin.include_role:
+    name: network.base.resource_manager
diff --git a/roles/run/tasks/includes/health_check.yaml b/roles/run/tasks/includes/health_check.yaml
index 8ccd20f..6c4447b 100644
--- a/roles/run/tasks/includes/health_check.yaml
+++ b/roles/run/tasks/includes/health_check.yaml
@@ -7,6 +7,6 @@
      health_checks: "{{ bgp_health | network.bgp.health_check_view(operation) }}"

 - name: BGP health checks
-  debug:
-     var: health_checks
   failed_when: "'unsuccessful' == health_checks.status"
+  ansible.builtin.debug:
+    var: health_checks
diff --git a/roles/run/tasks/includes/health_checks/eos.yaml b/roles/run/tasks/includes/health_checks/eos.yaml
index b43708c..b71a087 100644
--- a/roles/run/tasks/includes/health_checks/eos.yaml
+++ b/roles/run/tasks/includes/health_checks/eos.yaml
@@ -1,6 +1,6 @@
 ---
 - name: Parse bgp summary
-  cli_parse:
+  ansible.utils.cli_parse:
     command: "show ip bgp summary"
     parser:
       name: ansible.netcommon.content_templates
diff --git a/roles/run/tasks/includes/health_checks/iosxr.yaml b/roles/run/tasks/includes/health_checks/iosxr.yaml
index 2a6bca3..d2e66f2 100644
--- a/roles/run/tasks/includes/health_checks/iosxr.yaml
+++ b/roles/run/tasks/includes/health_checks/iosxr.yaml
@@ -1,6 +1,6 @@
 ---
 - name: Parse bgp summary
-  cli_parse:
+  ansible.utils.cli_parse:
     command: "show bgp summary"
     parser:
       name: ansible.netcommon.content_templates
diff --git a/roles/run/tasks/includes/health_checks/junos.yaml b/roles/run/tasks/includes/health_checks/junos.yaml
index bacc328..bf80e6c 100644
--- a/roles/run/tasks/includes/health_checks/junos.yaml
+++ b/roles/run/tasks/includes/health_checks/junos.yaml
@@ -8,5 +8,5 @@


 - name: Show Summary facts
-  debug:
+  ansible.builtin.debug:
     msg: "{{ bgp_health }}"
diff --git a/roles/run/tasks/includes/health_checks/vyos.yaml b/roles/run/tasks/includes/health_checks/vyos.yaml
index b43708c..b71a087 100644
--- a/roles/run/tasks/includes/health_checks/vyos.yaml
+++ b/roles/run/tasks/includes/health_checks/vyos.yaml
@@ -1,6 +1,6 @@
 ---
 - name: Parse bgp summary
-  cli_parse:
+  ansible.utils.cli_parse:
     command: "show ip bgp summary"
     parser:
       name: ansible.netcommon.content_templates
diff --git a/roles/run/tasks/main.yml b/roles/run/tasks/main.yml
index d460df0..1c397cd 100644
--- a/roles/run/tasks/main.yml
+++ b/roles/run/tasks/main.yml
@@ -1,6 +1,6 @@
 ---
 - name: Include tasks
-  include_tasks: includes/{{ operation.name }}.yaml
   loop: "{{ operations }}"
   loop_control:
     loop_var: operation
+  ansible.builtin.include_tasks: includes/{{ operation.name }}.yaml
    """})
    print(response["answer"])
    return response["answer"]
