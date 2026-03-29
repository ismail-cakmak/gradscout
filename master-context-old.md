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
  "tuition_fee": "Instruction: The total cost of the entire program. Example: '1500 EUR/semester' or 'Free'",
  "housing_info": "Instruction: Indicate if housing is guaranteed or supplied and average rent. Example: 'No guarantee, ~600 EUR/month'",
  "city": "Instruction: The city where the university is located. Example: 'Berlin'",
  "program_duration": "Instruction: How long the program takes. Example: '2 years', '18 months', '3 semesters'",
  "english_requirements": "Instruction: Whether they accept English bachelor's OR require test scores. Example: 'English bachelor's accepted OR IELTS 6.5, TOEFL 92'",
  "gmat_gre_requirements": "Instruction: Whether GMAT/GRE is required and minimum scores. Example: 'Not required' or 'GRE required, minimum 320'",
  "application_fee": "Instruction: The cost to apply. Example: '75 EUR' or 'Free'",
  "deadlines_for_intakes": "Instruction: Deadlines for each intake (Fall/Winter, Spring/Summer). Example: 'Fall (Sep) - deadline: March 15; Spring (Feb) - deadline: October 1'",
  "program_summary": "Instruction: Summary of topics covered, research areas, and professors in the field. Example: 'Machine learning, computer vision, NLP. Research labs: AI Lab, Data Science Group. Prof. Smith specializes in deep learning.'",
  "scholarship_info": "Instruction: Available scholarships, eligibility, AND their website links. Example: 'Merit scholarship: 50% tuition waiver (https://tum.de/scholarships). Also: diversity scholarship.'",
  "bachelor_requirements": "Instruction: Specific bachelor degree requirements, required courses, and credit requirements. Example: 'Bachelor in CS or related field. Required courses: Data Structures, Algorithms, Linear Algebra. Minimum 180 ECTS credits.'",
  "language_of_instruction": "Instruction: Specify if the program is 100% English or requires proficiency in the local language. Example: '100% English' or 'Requires A2 German by 2nd semester'.",
  "required_documents": "Instruction: List the specific documents required to apply. Example: 'CV, Letter of Motivation, 2 Letters of Recommendation, Transcript of Records.'",
  "work_experience_requirements": "Instruction: State if prior professional work experience is required and how much. Example: 'None required' or 'Minimum 1 year relevant work experience'.",
  "delivery_mode": "Instruction: Is the program On-Campus, Online, or Hybrid? Is it Full-Time or Part-Time? Example: 'Full-Time, On-Campus'.",
  "acceptance_rate_or_competitiveness": "Instruction: Any available information on acceptance rates, number of applicants vs. places, or quotes on how competitive the program is. Example: 'Highly competitive, ~15% acceptance rate' or 'Not specified'.",
  "career_prospects_data": "Instruction: Key statistics about graduate placement, such as average starting salary, employment rate within 6 months, or top hiring companies. Example: '95% employed in 3 months, top employers: Google, McKinsey'.",
  "pre_master_available": "Instruction: Does the university offer a pre-master or bridging program if the applicant lacks specific credits? Example: 'Yes, 30 ECTS bridging program available' or 'No, direct admission only'.",
  "application_process_steps": "Instruction: Outline the step-by-step admissions process after submitting the application. Example: 'Stage 1: Document screening. Stage 2: Online arithmetic/logic test. Stage 3: 30-minute academic interview. Final decision within 4 weeks.'",
  "program_flexibility": "Instruction: Does the program offer options to study part-time, spend a semester abroad (exchange), or complete a double degree? Example: 'Mandatory semester abroad; Double Degree with Sciences Po available'.",
  "industry_and_thesis_info": "Instruction: Does the program require a master's thesis? Can it be done in partnership with an industry company? Example: 'Requires 30 ECTS thesis, often done with partner companies like Siemens or BMW'.",
  "application_portal_type": "Instruction: Specify if the application is submitted directly to the university portal, or through a national/centralized system like Uni-Assist, Studielink, or UCAS. Example: 'Requires Uni-Assist first' or 'Direct university portal'.",
  "direct_application_link": "Instruction: The exact URL to start the application process or portal. Example: 'https://campus.tum.de/apply'.",
  "intake_semesters": "Instruction: Does the program start in Fall/Winter only, or is there a Spring/Summer intake? Example: 'Starts Winter (Oct 1) and Summer (April 1)'.",
  "deferral_policy": "Instruction: Can admission be deferred to the following year? Example: 'Admission can be deferred for up to 2 semesters'."
}
```

---

## Rules

- The Rank Cutoff applies strictly to QS World University Rankings or Times Higher Education (THE). Ignore national rankings, ARWU, US News, etc.
- Data must be saved as strict JSON files in `.state/extraction/` directory.
- Filename format: `universityname-programname.json`