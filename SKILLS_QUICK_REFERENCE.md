# Meta Business Agent Skills - Quick Reference

## 📋 Skills Cheat Sheet

### What are Skills?
**Behavioral instructions** that tell the agent HOW to act in specific situations.

**NOT facts/knowledge** (that goes in Knowledge section).

---

## 🚀 Quick Setup (3 methods)

### Method 1: Meta Business Suite (Visual) ⭐ Recommended
1. Go to [Meta Business Suite](https://business.facebook.com/)
2. All tools → **Meta Business Agent** → **Skills** tab
3. Click **+ Create skill**
4. Fill in: **Title**, **Description**, **Skill instructions**
5. Save & test in **Test chat**

### Method 2: Python Script (Automated)
```bash
# Upload all RSI skills
python skills_manager.py --upload

# List existing skills
python skills_manager.py --list
```

### Method 3: cURL (Manual API)
```bash
curl -X POST "https://api.facebook.com/{PHONE_NUMBER_ID}/agent_config/skills" \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Content-Type: application/json" \
  -H "X-API-Version: 2.0.0" \
  -d '{"title":"skill-name","description":"When to apply","skill":"Instructions"}'
```

---

## ⚠️ Title Rules (STRICT)

| ✅ Valid | ❌ Invalid |
|---------|-----------|
| `greeting-skill` | `Greeting Skill` (spaces) |
| `pricing-questions` | `greeting_skill` (underscores) |
| `refund-policy` | `Greeting-Skill` (capitals) |
| Lowercase only | Uppercase not allowed |
| Numbers OK: `faq-2024` | Special chars: `skill@home` |
| Hyphens OK: `a-b-c` | Spaces not allowed |
| Max 64 chars | Over 64 chars |

---

## 📏 Character Limits

| Field | Max Length |
|-------|-----------|
| Title | 64 chars (lowercase, numbers, hyphens only) |
| Description | 1,024 chars |
| Skill | 20,000 chars |

---

## 🎯 10 RSI Skills Summary

| # | Title | Triggered By | Emoji |
|---|-------|--------------|-------|
| 1 | `greeting-skill` | First message, "hola" | - |
| 2 | `circular-economy-questions` | "economía circular", "reciclaje" | ♻️ |
| 3 | `sustainability-questions` | "sostenibilidad", "ESG" | 🌱 |
| 4 | `csr-rsc-questions` | "RSC", "CSR", "ética" | 🤝 |
| 5 | `assignment-help` | "tarea", "entrega", "trabajo" | 📚 |
| 6 | `course-information` | "syllabus", "fechas", "profesor" | 📅 |
| 7 | `exam-preparation` | "examen", "test", "quiz" | 📝 |
| 8 | `examples-case-studies` | "ejemplos", "casos", "empresas" | 💡 |
| 9 | `unclear-or-offtopic` | Unclear/off-topic messages | - |
| 10 | `human-handoff` | "hablar con profesor", urgent | 👨‍🏫 |

---

## 🔧 API Operations

### Create
```bash
POST /{PHONE_NUMBER_ID}/agent_config/skills
Body: {"title":"...", "description":"...", "skill":"..."}
```

### List All
```bash
GET /{PHONE_NUMBER_ID}/agent_config/skills
```

### Get One
```bash
GET /{PHONE_NUMBER_ID}/agent_config/skills/{SKILL_ID}
```

### Update
```bash
PUT /{PHONE_NUMBER_ID}/agent_config/skills/{SKILL_ID}
Body: {"title":"...", "description":"...", "skill":"..."}
```

### Delete
```bash
DELETE /{PHONE_NUMBER_ID}/agent_config/skills/{SKILL_ID}
```

---

## ✅ Best Practices

### DO
- ✅ Use clear, numbered steps (1, 2, 3...)
- ✅ Start with 3-7 skills, add more later
- ✅ Test each skill in **Test chat** after creating
- ✅ Use **View sources** to see which skill activated
- ✅ Include examples in skill instructions
- ✅ Combine with **Knowledge** (facts) + **Personality** (tone)

### DON'T
- ❌ Create conflicting skills ("always escalate" vs "never escalate")
- ❌ Use uppercase or spaces in titles
- ❌ Mix behavior (skills) with facts (knowledge)
- ❌ Make skills too long (prefer 500-2000 chars)
- ❌ Forget to test after creating/editing

---

## 🧪 Testing Checklist

After uploading skills:

1. ✅ Go to **Meta Business Suite** → **Meta Business Agent** → **Test chat**
2. ✅ Test each skill:
   - Send message that should trigger it
   - Check response matches expected behavior
3. ✅ Click **View sources** to confirm correct skill activated
4. ✅ If not working: click **Reload** and try again
5. ✅ Adjust skill description or instructions if needed

---

## 📁 File Reference

| File | Purpose |
|------|---------|
| `skills_manager.py` | Python script to manage skills via API |
| `SKILLS_CONFIGURATION_GUIDE.md` | Complete guide (20+ pages) |
| `RSI_SKILLS_TEMPLATES.md` | All 10 skills ready to copy/paste |
| `SKILLS_QUICK_REFERENCE.md` | This cheat sheet |

---

## 🚨 Common Errors & Fixes

### "Invalid title"
**Fix:** Use only lowercase, numbers, hyphens. No spaces or underscores.

### "Skill not activating"
**Fix:** Make description more specific with keywords students actually use.

### "Two skills activating"
**Fix:** Make descriptions mutually exclusive. Use "ONLY when..." or "NOT when..."

### "Authentication failed"
**Fix:** Check `WHATSAPP_TOKEN` is valid. Add `X-API-Version: 2.0.0` header.

---

## 🔗 Required Environment Variables

```bash
PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_TOKEN=your_permanent_access_token
```

Get these from: [Meta Developer Dashboard](https://developers.facebook.com/) → Your App → WhatsApp → API Setup

---

## 📚 Skills vs Knowledge vs Personality

| Component | What It Does | Example |
|-----------|--------------|---------|
| **Skills** | Behavioral instructions (HOW to respond) | "When asked about pricing: 1) Ask location 2) Give base price" |
| **Knowledge** | Facts, data, documents (WHAT to say) | "Our price is $50" (uploaded PDFs, FAQs) |
| **Personality** | Overall tone (HOW to sound) | "Friendly, professional, concise" |

**Use all three together** for best results!

---

## 🎓 RSI Course Context

**Course:** Responsabilidad Social en la Industria  
**Semester:** Otoño 2026  
**Topics:** 
- Circular economy (economía circular)
- Industrial sustainability (sostenibilidad industrial)
- Corporate Social Responsibility (RSC)

**Agent Role:** Teaching assistant that helps students with concepts, assignments, and exam prep.

---

## 📞 Support

- **Meta API Docs:** https://developers.facebook.com/docs/whatsapp/business-management-api/agent-config
- **Meta Developer Community:** https://developers.facebook.com/community/
- **Script Issues:** Check logs in `skills_manager.py`

---

## ⚡ Quick Commands

```bash
# View predefined skills (no upload)
python skills_manager.py

# Upload all RSI skills to Meta
python skills_manager.py --upload

# List existing skills
python skills_manager.py --list

# Test the WhatsApp bot
python test_bot.py

# Run the WhatsApp bot
python app.py
```

---

**Version:** 1.0.0  
**Last Updated:** September 2026  
**Course:** RSI Otoño 2026
