# Update the existing GitHub repository without losing history

1. Download and extract the updated ZIP. Work from the **contents** of `neuromarketing-eye-tracking-heatmaps/`.
2. Before uploading, review `docs/PUBLICATION_AND_ETHICS.md` and confirm public redistribution rights for `data/public_recordings/`.
3. Clone your existing repository, rather than creating a new repository if you want to preserve its existing URL and commit history:

   ```bash
   git clone https://github.com/ravalpriyankm/Emotional-Heatmap-Generation-GUI-for-iMotion-for-Image-Based-Experiment.git
   cd Emotional-Heatmap-Generation-GUI-for-iMotion-for-Image-Based-Experiment
   ```

4. Copy the updated project files **into the root of this clone**, including hidden `.github` and `.gitignore`, replacing the old source code. **Do not overwrite `.git/`**.
5. The old `raw_data.zip`, `scrooling.zip` and outdated notebooks/code can be removed from the current working tree, but their earlier copies may remain permanently accessible in Git history. **Deleting them in a new commit does not remove earlier public data from the repository's history.**
6. If the historical archive contains information that must not remain publicly accessible, consult GitHub's guidance for removing sensitive data from a repository and coordinate with affected rights holders. Consider whether a fresh repository or history rewrite is appropriate. Do not rewrite history casually because it disrupts existing clones.
7. Before pushing, inspect changed files and commits:

   ```bash
   git status
   git diff --stat
   git add .
   git diff --cached --stat
   git commit -m "Refresh MSc neuromarketing research toolkit and publication data"
   git push
   ```

8. In the GitHub **About** sidebar set:
   - **Description:** `University of Essex MSc (2022-2023) neuromarketing research: offline iMotions gaze and facial-expression visualisation with a Python GUI.`
   - **Topics:** `neuromarketing`, `eye-tracking`, `imotions`, `heatmaps`, `python`, `human-computer-interaction`, `research`, `data-visualization`
9. Pin the updated repository on your GitHub profile when the README, data permissions and tests are confirmed.

**Important:** No direct change to the user's GitHub account has been made by this ZIP creation workflow.
