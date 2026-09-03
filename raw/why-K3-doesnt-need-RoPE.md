This is how I understand why K3 doesn't need RoPE where KDA basically encodes the positional information directly in the update rule. 

One can think of RoPE as a product of accumulating transition matrices applied to queries and keys. This is equivalent to taking the matrix power of the same static rotation matrix.   

In the linear attention literature, this can be generalized where the transition matrix changes at each position and becomes data-dependent.   

The 2 common perspectives of understanding DeltaNet are: 
- Some read + write operations with differing strengths  
- Online regression against the retrieval error with fast weights  

With this positional encoding perspective, we have a 3rd way to understand GDN. We can choose our transition matrix to be the generalized householder transform (as a type of erasing operation) and recover GDN.   

Importantly, the KDA update rule with general householder + the channelwise decay is NOT orthogonal.   

But, this framing allows us to relax the orthogonality constraint of the rotation matrix in RoPE since we have a single transform on both the queries and keys at once instead of the composition of 2 independent absolute position transforms

Why Kimi K3 doesn’t need RoPE

RoPE encodes relative position info: for any positions m and n, we need the transformations on query and key to cancel out into a relative position after doing q @ k.T
Math: R(m).T @ R(n) = R(n-m)

It is proven that any powers of orthogonal matrix (A^m) can be RoPE
Householder matrix, a type of matrix, satisfies the requirements
If you replace RoPE with Householder matrices, after 🧑‍🍳 hardcore math🧑‍🍳, DeltaNet pops out in the softmax attention formula
Crazy, I know. DeltaNet literally has a Householder matrix in it though

Kimi Delta Attention is a DeltaNet variant
Hence, KDA can replace RoPE
