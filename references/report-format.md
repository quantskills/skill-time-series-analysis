# Report Format

Use this compact structure:

```markdown
## Summary

| Metric | Value |
|---|---:|
| `n_obs` | ... |
| `trend_type` | ... |

## Evidence

### Distribution

KDE / QQ rows or chart links.

### Stationarity

Windowed Hurst / ADF / KPSS rows.

### Caveats

- Short sample, conflicting tests, non-positive values, or unstable residuals.
```

Keep the summary before evidence.
