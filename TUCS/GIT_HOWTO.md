###   Short instructions how to work with TUCS project in GIT


#### 1. Initialize account on gitlab

  Go to

https://gitlab.cern.ch/

  and login with your CERN username/password.


#### 2. Read ATLAS GIT tutorial

https://atlassoftwaredocs.web.cern.ch/gittutorial/

  It contains some basic info about GIT and explains how
  to work with Athena project.

  Our project - Tucs is independent from Athena and many things
  which are mentioned in tutorial are not applicable to out project,
  but still, you'll get basic ideas how to work with GIT.


#### 3. Fork Tucs repository

  Go to

https://gitlab.cern.ch/atlas-tile-offline/Tucs

  and press Fork button.


#### 4. Setup environment
```
ssh lxplus
setupATLAS
lsetup git
```

#### 5. Clone Tucs repository locally
```
git clone https://:@gitlab.cern.ch:8443/$USER/Tucs.git
cd Tucs
git remote add upstream https://:@gitlab.cern.ch:8443/atlas-tile-offline/Tucs.git
```

#### 6. Setup new development branch based on upstream/master
```
git fetch upstream
git checkout -b <YOUR_BRANCH_NAME_HERE> upstream/master --no-track
```
  instead of YOUR_BRANCH_NAME_HERE put some reasonable name for your branch,
  e.g. ${USER}-MinBias-dev or laser-test-branch.


#### 7. Develop the code, add new files etc

  To see your changes:
```
git status
git diff
```

#### 8. Prepare for commit
```
git status
git add <NAME_OF_MODIFIED_FILE>
git status
```

#### 9. Commit to local and then to remote repository
```
git commit
git push
```
  if you do "git push" for given branch for the first time,
  GIT will suggest you to write
```
git push --set-upstream origin <YOUR_BRANCH_NAME_HERE>
```

#### 10. Share your new code with other developers

  When the code is mature enough - request merge with master repository

  Go to the URL suggested by GIT

https://gitlab.cern.ch/USERNAME/Tucs/merge_requests/new?merge_request%5Bsource_branch%5D=YOUR_BRANCH_NAME_HERE

  and press button "Submit merge request".

  Merge request will be considered by Tucs Project Manager and eventually 
  approved. Once all your changes are merged, you can remove your branch
  from git or continue to use it. But in this case, to avoid conflicts
  in future merge requests - synchronize your branch with upstream/master
  from time to time.


#### 11. Retrieve updates from master repository

  If you want to update your code to the latest version of Tucs
  available in master/upstream branch, do the following:
```
git fetch upstream
git merge upstream/master
```
  or even better - rebase your branch
```
git fetch upstream
git rebase upstream/master
```
  Rebase approach is better if you didn't change anything in your branch and 
  simply want to refresh your installation and to use latest version from GIT.
  Also, it's good idea to rebase your private branch to upstream/master
  immediately after your merge request was accepted. But it's only needed if 
  you want to use the same branch name for several merge requests. Another 
  approach is to delete the branch after it was merged with upstream/master
  and to create new branch with new name for every new merge request.

  After "git merge" or "git rebase" you'll also need to put updated code to 
  your private repositories with
```
git commit
git push
```

#### 12. Special branches (a-la tags)

  From time to time new branches will be created in master repository
  They will be similar to SVN tags, e.g. Tucs-00-01-00 etc.
  These tags will be installed in tilebeam account and will be used
  by whole TileCal community.


-------------------------------------------------------------------------------

* This Howto was:
  - Written by Sanya Solodkov 27-07-2017,
  - Reviewed by Henric Wilkens 28-07-2017.
  - Amended by (no amendments yet)
