# Claude Code Setup (VS Code + AWS Bedrock)

**Quick guide**: Configure the Claude Code extension in VS Code to use the AWS Bedrock API key.

---

## What you need

The **API key** from the interviewer (a long random string). Don't use your own Google or Anthropic key.

---

## Option A: Set the key in the terminal, then open VS Code from that terminal

### Windows (PowerShell)

1. Open **PowerShell** (Start menu → type "PowerShell" → open it)
2. Run this command (replace `YOUR_KEY_HERE` with the actual key):

```powershell
$env:AWS_BEARER_TOKEN_BEDROCK = "YOUR_KEY_HERE"
```

3. Then start VS Code from the same PowerShell window:

```powershell
code "C:\Users\avivmo\code\idit\fiverr"
```

(Or if you're already in the project folder, just run `code .`)

### Windows (Command Prompt / CMD)

1. Open **CMD**
2. Run (replace `YOUR_KEY_HERE` with the real key):

```cmd
set AWS_BEARER_TOKEN_BEDROCK=YOUR_KEY_HERE
```

3. Then from the same CMD window:

```cmd
code "C:\Users\avivmo\code\idit\fiverr"
```

### Mac / Linux (Terminal)

1. Open **Terminal**
2. Run (replace `YOUR_KEY_HERE` with the real key):

```bash
export AWS_BEARER_TOKEN_BEDROCK="YOUR_KEY_HERE"
```

3. From the same terminal:

```bash
code ~/path/to/fiverr
```

**Important**: If you close that terminal and open VS Code some other way (e.g. double-clicking), the key won't be set anymore. For permanent setup, use Option B.

---

## Option B: Set the key in VS Code so it's saved

1. In VS Code, press **Ctrl+Shift+P** (Command Palette)
2. Type: `Open User Settings (JSON)` and press Enter
3. Add this to your `settings.json` (replace `YOUR_KEY_HERE` with the real key):

```json
"claude-code.environmentVariables": {
  "AWS_BEARER_TOKEN_BEDROCK": "YOUR_KEY_HERE"
}
```

(If there's already other content, add a comma before this block)

4. **Save** the file
5. **Restart VS Code** once

**Note**: If the extension uses a different setting name, search in Settings (Ctrl+,) for "Claude" or "Bedrock" and paste the key in the API key field the extension shows.

---

## Check that it worked

1. In VS Code, press **Ctrl+Shift+P** (Command Palette)
2. Type "Claude" or "Start chat" and run the Claude Code command
3. If it opens and doesn't say "authentication failed" or "invalid key", the key is set correctly

---

## Optional tip

When chatting with Claude, you can @-mention or paste the project's `CLAUDE.md` file so Claude follows the same code style and dependencies.

---

## References

- [AWS Bedrock API keys](https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys-use.html)
- [Claude Code + Bedrock guidance](https://github.com/aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock)
