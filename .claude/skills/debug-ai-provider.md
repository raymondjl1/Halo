---
name: debug-ai-provider
description: Debug AI provider failures including Ollama, Claude API, OpenAI. Triggers when investigating model timeouts, circuit breaker trips, GPU issues, or inference failures.
---

# Debug AI Provider

## Steps

1. **Check provider status**:
   ```python
   providers = self.env['halo.ai.provider'].search([])
   for p in providers:
       print(f"{p.name}: circuit={p.circuit_state}, failures={p.failure_count}")
   ```

2. **Check Ollama** (local):
   ```sh
   docker compose ps ollama                    # Is it running?
   docker compose exec ollama ollama list       # Models loaded?
   docker compose logs -f ollama               # Errors?
   nvidia-smi                                  # GPU VRAM usage?
   curl http://localhost:11434/api/tags         # API responding?
   ```

3. **Test inference manually**:
   ```sh
   curl http://localhost:11434/api/generate \
     -d '{"model": "mistral:latest", "prompt": "Hello", "stream": false}'
   ```

4. **Check cloud providers** (Claude/OpenAI):
   - Verify API key in Odoo: Settings → Technical → System Parameters
   - Check provider status pages (status.anthropic.com, status.openai.com)
   - Test with curl using the API key

5. **Circuit breaker recovery**:
   - Circuit OPEN → wait 30s for auto-reset to HALF_OPEN
   - Or manually: set `circuit_state = 'closed'`, `failure_count = 0` on provider record

6. **GPU OOM (Ollama)**:
   ```sh
   docker compose restart ollama    # Free GPU memory
   nvidia-smi                       # Verify VRAM freed
   ```

7. **Common issues**:
   | Symptom | Cause | Fix |
   |---------|-------|-----|
   | All providers circuit OPEN | Cascade failure | Restart Ollama, verify API keys |
   | Timeout on large context | Model overloaded | Reduce context size, use smaller model |
   | Invalid JSON from Ollama | Model doesn't support JSON mode | Switch to model that does |
   | 429 from Claude/OpenAI | Rate limit hit | Reduce request rate, add delay |
