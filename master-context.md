# Master Context

## User Criteria

### Interest Keywords
cs, ai, ml, human computer interaction, hci, robotics, management, business, innovation

### Negative Keywords
education, social sciences, psychology, chemistry

### Target Countries
Germany

### Rank Cutoff
Top 50 (QS World University Rankings or Times Higher Education)

---

## Extraction Schema

```json
{
  "program_name": "Instruction: The official name of the degree. Example: 'MSc Computer Science'",
  "application_deadline": "Instruction: The exact date applications close for international students. Example: '2025-05-31'",
  "application_start_deadline": "Instruction: The date applications open for international students. Example: '2025-01-15'",
  "tuition_fee": "Instruction: The total cost of the entire program. Example: '1500 EUR/semester' or 'Free'",
  "housing_info": "Instruction: Indicate if housing is guaranteed and average rent. Example: 'No guarantee, ~600 EUR/month'",
  "city": "Instruction: The city where the university is located. Example: 'Berlin'"
}
```

---

## Rules

- The Rank Cutoff applies strictly to QS World University Rankings or Times Higher Education (THE). Ignore national rankings, ARWU, US News, etc.
- Data must be saved as strict JSON files in `.state/extraction/` directory.
- Filename format: `universityname-programname.json`