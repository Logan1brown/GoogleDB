# Code Edit Best Practices

## Precise Content Replacement

When using code edit tools like `replace_file_content`, it's critical to follow these steps to avoid mistakes:

1. Use `view_file` to see the exact content first
2. Copy the content precisely in the `TargetContent` parameter
3. Make careful modifications for the `ReplacementContent`

This is important because trying to reconstruct code from memory often leads to subtle mistakes, like:
- Missing styling parameters (e.g., forgetting `type="primary"`)
- Different button labels (e.g., "Add" vs "Add Member")
- Missing layout options (e.g., forgetting `use_container_width=True`)
- Missing spacing elements (e.g., forgetting `st.write("")` for vertical spacing)

By viewing and copying the exact content first, we ensure that only the intended changes are made while preserving all other aspects of the code.
