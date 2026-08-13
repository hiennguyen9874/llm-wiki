# Create workspace buffer
workspace = torch.empty(...)
seqlen_info.init()

# Compile: create CUDAGraphs
graphs = []
for task_info in task_infos:
  # Init: compile kernels according to spec
  attn = AttentionWrapper(attn_spec, task_info, workspace)
  g = torch.cuda.CUDAGraph()
  # Dummy plan
  attn.plan(seqlen_info)
  # Capture CUDA graphs
  with torch.cuda.graph(g):
    for i, layer in enumerate(layers):
      ...
      attn.run(...)
      ...
  graphs.append(g)

# Runtime: select the best CUDAGraph
g = select_graph(graphs)
finished = False
# Text generation loop
while not finished:
  seqlen_info.update()
  # Plan per generation step
  attn.plan(seqlen_info)
  # Replay CUDA-Graph
  g.replay()
