# Same-render two-stamp package (work order B) and the wrong turn that followed
#
# secL9f_RED_at_24141c0.txt   new gate check at the code of 24141c0: the archiving-stamp code refuses the
#                            same-render package (16/17)
# secL9f_GREEN_worktree.txt  the same check under the FIRST expectation (archiving-stamp code accepted):
#                            green on the working tree that became 37691b7 — an expectation later judged wrong
# battery_Vwork_summary.tsv  full offline battery of that working tree: 203/205, test_audit_r28_gate.py red
# r28gate_Vwork_excerpt.txt  the three red R28 gate lines (D6a/D6b/D7a) of that battery, excerpted
# ci_jobs_45348011655.txt    CI at 37691b7: both test jobs failed (gates job green)
# r28gate_V2worktree.txt     R28 gate at the corrected working tree: 37/37
# secL9_V2worktree.txt       R32 gate section L at the corrected working tree: 18/18 (L9f refusal + L9f2 override)
# ci_jobs_45351387852.txt    CI at cf33de3: three jobs success
# wreplay_B_*                replays of the 24141c0 B package that triggered the finding
