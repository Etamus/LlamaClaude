const errorMsg = '400 {"error":{"code":400,"message":"request (20680 tokens) exceeds the available context size (8192 tokens)","type":"exceed_context_size_error","n_prompt_tokens":20680,"n_ctx":8192}}'

const nPromptMatch = errorMsg.match(/"n_prompt_tokens"\s*:\s*(\d+)/)
const nCtxMatch    = errorMsg.match(/"n_ctx"\s*:\s*(\d+)/)
console.log('n_prompt_tokens:', nPromptMatch?.[1])
console.log('n_ctx:          ', nCtxMatch?.[1])

const matches = !!(nPromptMatch && nCtxMatch)
if (matches) {
  const inputTokens  = parseInt(nPromptMatch[1], 10)
  const contextLimit = 32768
  const avail        = Math.max(0, contextLimit - inputTokens - 1000)
  const adjusted     = Math.max(3000, avail)
  console.log('inputTokens:      ', inputTokens)
  console.log('availableContext: ', avail)
  console.log('adjustedMaxTokens:', adjusted)
  console.log('total (input+out):', inputTokens + adjusted, '<= 32768?', (inputTokens + adjusted) <= contextLimit)
} else {
  console.log('FALHOU: regex nao encontrou os campos')
}
