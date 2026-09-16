from app.resume.resume_parsers.pdf_parser import get_resume_text
from app.resume.resume_parsers.resume_parser import parse_resume

from app.Job_description.jd_parser import parse_jd

from app.exact_matcher import exact_match, match_requirements
from app.semantic_matcher import semantic_match

from samples.jd import jd


def main():

    # ========================================================
    # RESUME
    # ========================================================

    print("\n" + "=" * 60)
    print("RESUME")
    print("=" * 60)

    resume_text = get_resume_text()

    print("\nEXTRACTED RESUME TEXT\n")
    print(resume_text)

    parsed_resume = parse_resume(resume_text)

    print("\n" + "=" * 60)
    print("PARSED RESUME")
    print("=" * 60)

    print("\nName:")
    print(parsed_resume.get("name", ""))

    print("\nContact:")
    print(parsed_resume.get("contact", {}))

    print("\nSkills:")
    print(parsed_resume.get("skills", []))

    print("\nExperience:")
    for experience in parsed_resume.get("experience", []):
        print(experience)

    print("\nProjects:")
    for project in parsed_resume.get("projects", []):
        print(project)

    print("\nEducation:")
    for education in parsed_resume.get("education", []):
        print(education)

    print("\nEvidence:")
    for evidence in parsed_resume.get("evidence", []):
        print(evidence)


    # ========================================================
    # JOB DESCRIPTION
    # ========================================================

    print("\n" + "=" * 60)
    print("JOB DESCRIPTION")
    print("=" * 60)

    parsed_jd = parse_jd(jd)

    print("\nTitle:")
    print(parsed_jd.get("title", ""))

    print("\nRequirements:")
    for requirement in parsed_jd.get("requirements", []):
        print(requirement)

    print("\nRequired Skills:")
    print(parsed_jd.get("required_skills", []))

    print("\nPreferred Skills:")
    print(parsed_jd.get("preferred_skills", []))

    print("\nRequired Years:")
    print(parsed_jd.get("required_years"))

    print("\nExperience Required:")
    print(parsed_jd.get("experience_required"))

    print("\nEducation Required:")
    print(parsed_jd.get("education_required"))

    print("\nSections:")
    for section, items in parsed_jd.get("sections", {}).items():

        print(f"\n{section.upper()}:")

        for item in items:
            print(f"- {item}")


    # ========================================================
    # EXACT MATCHING
    # ========================================================

    print("\n" + "=" * 60)
    print("EXACT SKILL MATCHING")
    print("=" * 60)

    exact_results = exact_match(
        resume_skills=parsed_resume.get("skills", []),
        jd_required_skills=parsed_jd.get("required_skills", []),
        jd_preferred_skills=parsed_jd.get("preferred_skills", []),
    )

    print("\nMatched Required Skills:")
    print(exact_results["matched_required"])

    print("\nMissing Required Skills:")
    print(exact_results["missing_required"])

    print("\nMatched Preferred Skills:")
    print(exact_results["matched_preferred"])

    print("\nMissing Preferred Skills:")
    print(exact_results["missing_preferred"])

    print("\nRequired Skill Score:")
    print(f'{exact_results["required_score"]}%')

    print("\nPreferred Skill Score:")
    print(f'{exact_results["preferred_score"]}%')


    # ========================================================
    # REQUIREMENT-LEVEL EXACT MATCHING
    # ========================================================

    print("\n" + "=" * 60)
    print("REQUIREMENT-LEVEL EXACT MATCHING")
    print("=" * 60)

    requirement_results = match_requirements(
        resume=parsed_resume,
        jd_requirements=parsed_jd.get("requirements", []),
    )

    for result in requirement_results:

        print("\n" + "-" * 60)

        print(f'ID: {result["id"]}')

        print(f'Requirement: {result["text"]}')

        print(f'Type: {result["type"]}')

        print(f'Importance: {result["importance"]}')

        print(f'Skills: {result["skills"]}')

        print("\nExact Match:")
        print(
            f'  Matched: '
            f'{result["exact_match"]["matched_skills"]}'
        )

        print(
            f'  Missing: '
            f'{result["exact_match"]["missing_skills"]}'
        )

        print(f'\nStatus: {result["status"]}')

        print(f'Match Score: {result["match_score"]}')

        print("\nEvidence:")

        if result["evidence"]:

            for evidence in result["evidence"]:
                print(
                    f'  - {evidence["text"]}'
                )
                print(
                    f'    Source: {evidence["source"]}'
                )
                print(
                    f'    Matched Skills: '
                    f'{evidence["matched_skills"]}'
                )

        else:

            print("  No exact evidence found.")


    # ========================================================
    # SEMANTIC MATCHING
    # ========================================================

    print("\n" + "=" * 60)
    print("SEMANTIC MATCHING")
    print("=" * 60)

    semantic_results = semantic_match(
        resume=parsed_resume,
        jd=parsed_jd,
        top_k=3,
    )

    for result in semantic_results:

        print("\n" + "-" * 60)

        print(
            f'Requirement ID: '
            f'{result["requirement_id"]}'
        )

        print(
            f'Requirement: '
            f'{result["requirement"]}'
        )

        print(
            f'Type: '
            f'{result["requirement_type"]}'
        )

        print(
            f'Importance: '
            f'{result["importance"]}'
        )

        print(
            f'Skills: '
            f'{result["skills"]}'
        )

        print(
            f'Threshold: '
            f'{result["threshold"]}'
        )

        print(
            f'Best Similarity: '
            f'{result["best_similarity"]}'
        )

        print(
            f'Has Semantic Evidence: '
            f'{result["has_semantic_evidence"]}'
        )

        print("\nSemantic Evidence:")

        if result["semantic_evidence"]:

            for evidence in result["semantic_evidence"]:

                print(
                    f'  - {evidence["text"]}'
                )

                print(
                    f'    Source: '
                    f'{evidence["source"]}'
                )

                print(
                    f'    Similarity: '
                    f'{evidence["similarity"]}'
                )

                print(
                    f'    Retrieval Score: '
                    f'{evidence["retrieval_score"]}'
                )

        else:

            print("  No semantic evidence above threshold.")


if __name__ == "__main__":
    main()