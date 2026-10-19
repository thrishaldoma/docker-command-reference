KUBERNETES / KUBECTL COMMAND REFERENCE

commands.txt   Built-in command names and descriptions from the installed client.
examples.txt   Practical commands with values, options and one-line explanations.
reference.txt  Complete recursive --help output, including usage, flags, defaults
               and upstream examples; kubectl options lists shared global flags.
catalog.json   Client version, generation time, command counts and scope.

The help snapshot normalizes local home paths to $HOME and removes trailing
whitespace. Original command descriptions and usage text are otherwise retained.

Refresh the generated files from the repository root:
  python3 scripts/generate_kubectl_reference.py

Generation uses an empty kubeconfig and read-only help/client-version commands.
It does not connect to a cluster or change Kubernetes resources.

For examples, replace POD, NODE, CONTEXT, resource names, image tags and paths
with your own values. Create the demo namespace before using -n demo. Examples
are independent recipes, not a script to execute from top to bottom. Commands
without -n use the namespace configured in the selected context. Image tags
such as stable are examples; use a suitable pinned version for your workload.

Cluster commands require an accessible API server and appropriate permissions.
Available APIs depend on the server version, installed CRDs and controllers.
Plugin commands are not included in the generated built-in command catalog.
See the selected command's help for required positional arguments. Delete,
rollout, scale, patch, apply and node-maintenance examples change live resources.

Official documentation and attribution:
  https://kubernetes.io/docs/reference/kubectl/
  https://kubernetes.io/docs/reference/kubectl/generated/
  https://kubernetes.io/docs/reference/kubectl/quick-reference/
Generated descriptions and help come from kubectl, maintained by the Kubernetes
authors under Apache-2.0. The license is included in LICENSE.txt; upstream:
  https://github.com/kubernetes/kubectl/blob/master/LICENSE
