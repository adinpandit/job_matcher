"""Focused tests for shared skill matching and JD skill extraction.

Run from the repo root:

    python -m unittest tests.test_skill_extraction -v
"""

import unittest

from app.skills import find_skills
from app.Job_description.jd_parser import parse_jd
from app.Job_description.jd_skill_extractor import extract_jd_skills
from app.resume.resume_skills.skill_extractor import extract_skill


SAMPLE_JD = """Senior Backend Engineer

Responsibilities
Design services in Go and keep systems reliable.

Required Skills
Strong programming skills in Python.
Experience with FastAPI and Docker.
Solid knowledge of C++ and Node.js.

Preferred Qualifications
Experience with PostgreSQL and LangChain.
Familiarity with scikit-learn.
"""


class FindSkillsTests(unittest.TestCase):
    def test_python_is_matched(self):
        self.assertIn("python", find_skills("Strong programming skills in Python."))

    def test_java_does_not_match_javascript(self):
        found = find_skills("Expert in JavaScript and TypeScript.")
        self.assertIn("javascript", found)
        self.assertNotIn("java", found)

    def test_java_still_matches_on_its_own(self):
        self.assertIn("java", find_skills("Backend written in Java and Kotlin."))

    def test_cpp_is_matched_despite_regex_special_chars(self):
        self.assertIn("c++", find_skills("Systems programming in C++ for 5 years."))

    def test_cpp_not_matched_inside_larger_token(self):
        self.assertNotIn("c++", find_skills("We use c++11 and c++17."))

    def test_nodejs_is_matched(self):
        self.assertIn("node.js", find_skills("APIs built with Node.js and Express."))

    def test_nodejs_dot_is_literal_not_wildcard(self):
        self.assertNotIn("node.js", find_skills("nodexjs is not a real thing"))

    def test_empty_text_returns_empty_list(self):
        self.assertEqual(find_skills(""), [])
        self.assertEqual(find_skills(None), [])

    def test_result_order_follows_canonical_list(self):
        found = find_skills("Docker, Python, FastAPI")
        self.assertEqual(found, sorted(found, key=self._canonical_index))

    @staticmethod
    def _canonical_index(skill):
        from app.skills import SKILLS
        return SKILLS.index(skill)


class ExtractJdSkillsTests(unittest.TestCase):
    def setUp(self):
        self.sections = parse_jd(SAMPLE_JD)["sections"]
        self.result = extract_jd_skills(self.sections)

    def test_return_structure_is_preserved(self):
        self.assertEqual(set(self.result), {"required_skills", "preferred_skills"})

    def test_required_skills_come_from_requirements_section(self):
        required = self.result["required_skills"]
        self.assertEqual(
            set(required), {"python", "fastapi", "docker", "c++", "node.js"}
        )

    def test_preferred_skills_come_from_preferred_section(self):
        preferred = self.result["preferred_skills"]
        self.assertEqual(set(preferred), {"postgresql", "langchain", "scikit-learn"})

    def test_required_and_preferred_do_not_bleed_together(self):
        self.assertNotIn("langchain", self.result["required_skills"])
        self.assertNotIn("python", self.result["preferred_skills"])

    def test_parse_jd_return_structure_is_preserved(self):
        parsed = parse_jd(SAMPLE_JD)
        self.assertEqual(
            set(parsed),
            {
                "title",
                "required_skills",
                "preferred_skills",
                "required_years",
                "experience_required",
                "education_required",
                "sections",
            },
        )


class ResumeSkillExtractorTests(unittest.TestCase):
    def test_uses_shared_vocabulary_and_boundaries(self):
        resume = {"skills": "Python, JavaScript, C++, Node.js, scikit-learn"}
        found = extract_skill(resume)
        self.assertIn("python", found)
        self.assertIn("javascript", found)
        self.assertIn("c++", found)
        self.assertIn("node.js", found)
        self.assertIn("scikit-learn", found)
        self.assertNotIn("java", found)

    def test_missing_skills_section_returns_empty(self):
        self.assertEqual(extract_skill({}), [])


if __name__ == "__main__":
    unittest.main()
