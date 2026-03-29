# Master Context

## User Criteria

### Interest Keywords
cs, ai, ml, human computer interaction, hci, robotics, management, business, innovation, informatics

### Negative Keywords
education, social sciences, psychology, chemistry, econ, economics, medical, biomedical, Linguistics

### Target Countries
Germany, Netherlands, France, United Kingdom, Ireland, Sweden, Switzerland, Finland, Denmark

### Rank Cutoff
Top 200 (QS World University Rankings or Times Higher Education)

---

## Extraction Schema

```json
{
  "program_url": "Instruction: The direct URL to the main program overview page. Example: 'https://www.tum.de/msc-computer-science'",
  "program_name": "Instruction: The official name of the degree. Example: 'MSc Computer Science'",
  "deadlines_for_intakes": "Instruction: Deadlines for each intake (Fall/Winter, Spring/Summer). Example: 'Fall (Sep) - deadline: March 15; Spring (Feb) - deadline: October 1'",
  "language_of_instruction": "Instruction: Specify if the program is 100% English or requires proficiency in the local language. Example: '100% English' or 'Requires A2 German by 2nd semester'.",
  "bachelor_requirements": "Instruction: Specific bachelor degree requirements, required courses, and credit requirements. Example: 'Bachelor in CS or related field. Required courses: Data Structures, Algorithms, Linear Algebra. Minimum 180 ECTS credits.'"
}
```

---

## Rules

- The Rank Cutoff applies strictly to QS World University Rankings or Times Higher Education (THE). Ignore national rankings, ARWU, US News, etc.
- Data must be saved as strict JSON files in `.state/extraction/` directory.
- Filename format: `universityname-programname.json`