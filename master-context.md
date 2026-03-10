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
  "program_name": "Instruction: The official name of the degree. Example: 'MSc Computer Science'",
  "application_deadline": "Instruction: The exact date applications close for international students. Example: '2025-05-31'",
  "application_start_deadline": "Instruction: The date applications open for international students. Example: '2025-01-15'",
  "tuition_fee": "Instruction: The total cost of the entire program. Example: '1500 EUR/semester' or 'Free'",
  "housing_info": "Instruction: Indicate if housing is guaranteed or supplied and average rent. Example: 'No guarantee, ~600 EUR/month'",
  "city": "Instruction: The city where the university is located. Example: 'Berlin'",
  "program_duration": "Instruction: How long the program takes. Example: '2 years', '18 months', '3 semesters'",
  "english_requirements": "Instruction: Whether they accept English bachelor's OR require test scores. Example: 'English bachelor's accepted OR IELTS 6.5, TOEFL 92'",
  "gmat_gre_requirements": "Instruction: Whether GMAT/GRE is required and minimum scores. Example: 'Not required' or 'GRE required, minimum 320'",
  "application_fee": "Instruction: The cost to apply. Example: '75 EUR' or 'Free'",
  "intake_and_deadline": "Instruction: When the program starts and application deadline. Example: 'Fall (Sep) - deadline: March 15; Spring (Feb) - deadline: October 1'",
  "program_summary": "Instruction: Summary of topics covered, research areas, and professors in the field. Example: 'Machine learning, computer vision, NLP. Research labs: AI Lab, Data Science Group. Prof. Smith specializes in deep learning.'",
  "scholarship_info": "Instruction: Available scholarships and eligibility. Example: 'Merit scholarship: 50% tuition waiver, deadline Feb 1. Also available: diversity scholarship, need-based aid.'",
  "bachelor_requirements": "Instruction: Specific bachelor degree requirements, required courses, and credit requirements. Example: 'Bachelor in CS or related field. Required courses: Data Structures, Algorithms, Linear Algebra. Minimum 180 ECTS credits.'"
}
```

---

## Rules

- The Rank Cutoff applies strictly to QS World University Rankings or Times Higher Education (THE). Ignore national rankings, ARWU, US News, etc.
- Data must be saved as strict JSON files in `.state/extraction/` directory.
- Filename format: `universityname-programname.json`