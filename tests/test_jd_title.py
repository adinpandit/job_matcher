"""Focused tests for extract_job_title / parse_jd()["title"].

Run from the repo root:

    python -m unittest tests.test_jd_title -v
"""

import unittest

from app.Job_description.jd_parser import parse_jd, extract_job_title
from samples.jd import jd as SAMPLE_JD


class JobTitleTests(unittest.TestCase):
    def test_sample_jd_role_from_intro_sentence(self):
        # The exact reported case: intro paragraph, no explicit "Job Title:" line.
        self.assertEqual(parse_jd(SAMPLE_JD)["title"], "AI/ML Backend Engineering Intern")

    def test_intro_paragraph_is_not_returned_whole(self):
        title = parse_jd(SAMPLE_JD)["title"]
        self.assertLess(len(title), 60)
        self.assertNotIn("We are looking for", title)

    def test_explicit_job_title_heading_is_preserved(self):
        text = "Job Title: Staff Platform Engineer\n\nWe are looking for an SRE to help.\n"
        self.assertEqual(extract_job_title(text), "Staff Platform Engineer")

    def test_explicit_position_heading_is_preserved(self):
        text = "Position: Data Scientist II\n\nResponsibilities\nBuild models.\n"
        self.assertEqual(extract_job_title(text), "Data Scientist II")

    def test_explicit_role_heading_is_preserved(self):
        text = "Role: Backend Engineer\nWe are hiring a backend engineer to scale things.\n"
        self.assertEqual(extract_job_title(text), "Backend Engineer")

    def test_section_heading_is_not_treated_as_title(self):
        text = "Responsibilities\nWrite code.\n\nRequirements\nPython.\n"
        self.assertNotIn(extract_job_title(text).lower(), {"responsibilities", "requirements"})

    def test_seeking_phrasing_is_supported(self):
        text = "Acme is seeking a Senior Machine Learning Engineer to join the team.\n"
        self.assertEqual(extract_job_title(text), "Senior Machine Learning Engineer")


if __name__ == "__main__":
    unittest.main()
