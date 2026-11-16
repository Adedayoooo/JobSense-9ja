from src.analyzers import ask, analyze_job_description, analyze_cv
from src.rag import retrieve_company_context

def analyze_gap(jd_analysis: dict, cv_analysis: dict) -> dict:
    """
    Compares what the job wants vs what the candidate has.
    Returns match score, missing skills, and LLM advice.
    """
    jd_skills = set(s.lower() for s in jd_analysis.get("required_skills", []))
    cv_skills = set(s.lower() for s in cv_analysis.get("technical_skills", []))

    matched = jd_skills & cv_skills
    missing = jd_skills - cv_skills   
    skill_score = (len(matched) / len(jd_skills) * 100) if jd_skills else 50

    jd_years = jd_analysis.get("experience_years_required", 0)
    cv_years = cv_analysis.get("total_experience_years", 0)
    gap_years = jd_years - cv_years

    if gap_years > 2:
        penalty = 20
    elif gap_years > 0:
        penalty = 10
    else:
        penalty = 0

    final_score = max(0, min(100, skill_score - penalty))

    prompt = f"""
A candidate is applying for a job. Here is the analysis:

Job requires: {jd_analysis.get("required_skills")}
Job seniority: {jd_analysis.get("seniority")}
Years required: {jd_years}

Candidate has: {cv_analysis.get("technical_skills")}
Candidate experience: {cv_years} years
Candidate strengths: {cv_analysis.get("strengths")}
Candidate gaps: {cv_analysis.get("gaps")}

Matched skills: {list(matched)}
Missing skills: {list(missing)}
Match score: {final_score:.0f}%

Return JSON with these fields:
{{
    "verdict": "Strong Match or Decent Match or Stretch Role or Unlikely Match",
    "should_apply": true or false,
    "one_line_summary": "one honest sentence about fit",
    "quick_wins": ["things candidate can add to CV to look stronger for THIS role"],
    "honest_advice": "2 sentences of real advice about whether and how to apply"
}}
"""
    llm_verdict = ask(prompt, temperature=0.2, as_json=True)

    return {
        "match_score":     round(final_score),
        "matched_skills":  sorted(list(matched)),
        "missing_skills":  sorted(list(missing)),
        "experience_gap":  gap_years,
        "verdict":         llm_verdict.get("verdict"),
        "should_apply":    llm_verdict.get("should_apply"),
        "one_line_summary": llm_verdict.get("one_line_summary"),
        "quick_wins":      llm_verdict.get("quick_wins", []),
        "honest_advice":   llm_verdict.get("honest_advice"),
    }

def generate_cover_letter(
    jd_analysis: dict,
    cv_analysis: dict,
    gap_analysis: dict
) -> str:
    """
    Writes a tailored cover letter using JD data, CV data,
    gap analysis, and company context from RAG.
    """
    company = jd_analysis.get("company_name", "the company")
    role    = jd_analysis.get("role_title", "the role")

    company_context = retrieve_company_context(company, role)

    prompt = f"""
You are an expert career coach writing a cover letter for a
Nigerian ML engineer applying for a job.

Write a cover letter that is:
- Specific to THIS company and THIS role (not generic)
- Honest about experience level (don't overclaim)
- Focused on impact and results, not just skills listed
- Professional but confident — not stiff or robotic
- Maximum 4 paragraphs
- NO clichés like "I am writing to express my interest"

INFORMATION TO USE:

About the role:
- Company: {company}
- Role: {role}
- They need: {jd_analysis.get("required_skills")}
- Key responsibilities: {jd_analysis.get("key_responsibilities")}
- Seniority: {jd_analysis.get("seniority")}

About the candidate:
- Name: {cv_analysis.get("candidate_name")}
- Skills: {cv_analysis.get("technical_skills")}
- Projects: {[p.get("name") + ": " + p.get("description", "")
              for p in cv_analysis.get("projects", [])]}
- Strengths: {cv_analysis.get("strengths")}
- Education: {cv_analysis.get("education")}

Match analysis:
- Score: {gap_analysis.get("match_score")}%
- Matched skills: {gap_analysis.get("matched_skills")}
- Honest advice: {gap_analysis.get("honest_advice")}

Company intelligence from knowledge base:
{company_context}

Write ONLY the cover letter body.
No subject line. No date.
Start with "Dear Hiring Manager" or the specific team if known.
"""
    return ask(prompt, temperature=0.7)

def jobsense(job_description: str, cv_text: str) -> dict:
    """
    The main function. Takes raw text, returns complete package.

    Flow:
        raw JD text  → analyze_job_description() → structured dict
        raw CV text  → analyze_cv()               → structured dict
        both dicts   → analyze_gap()              → score + advice
        all three    → generate_cover_letter()    → tailored letter
    """
    print("🔍 Analyzing job description...")
    jd = analyze_job_description(job_description)

    print("📄 Analyzing CV...")
    cv = analyze_cv(cv_text)

    print("📊 Calculating match...")
    gap = analyze_gap(jd, cv)

    print("✍️  Writing cover letter...")
    letter = generate_cover_letter(jd, cv, gap)

    print("✅ Done!\n")

    return {
        "job":          jd,
        "candidate":    cv,
        "gap":          gap,
        "cover_letter": letter,
    }

def print_report(output: dict):
    """Prints a readable report from jobsense() output."""
    gap = output["gap"]
    job = output["job"]

    score  = gap["match_score"]
    filled = score // 10
    bar    = "█" * filled + "░" * (10 - filled)
    emoji  = "🟢" if score >= 70 else ("🟡" if score >= 50 else "🔴")

    print(f"\n{'='*60}")
    print(f"  JOBSENSE NIGERIA — APPLICATION REPORT")
    print(f"{'='*60}")
    print(f"  Role   : {job['role_title']} @ {job['company_name']}")
    print(f"  Match  : {emoji} {score}%  {bar}")
    print(f"  Verdict: {gap['verdict']}")
    print(f"{'='*60}")

    print(f"\n✅ SKILLS YOU HAVE ({len(gap['matched_skills'])}):")
    for s in gap["matched_skills"]:
        print(f"   ✓ {s}")

    print(f"\n❌ MISSING SKILLS ({len(gap['missing_skills'])}):")
    for s in gap["missing_skills"]:
        print(f"   ✗ {s}")

    print(f"\n⚡ QUICK WINS:")
    for w in gap["quick_wins"]:
        print(f"   → {w}")

    print(f"\n🎯 HONEST ADVICE:")
    print(f"   {gap['honest_advice']}")

    print(f"\n{'='*60}")
    print(f"  COVER LETTER")
    print(f"{'='*60}")
    print(output["cover_letter"])
    print(f"{'='*60}\n")
