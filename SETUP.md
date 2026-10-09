# Setup (about 10 minutes, one time)

## Part A: upload the normal files
1. Open github.com/MadhavGarg98/MadhavGarg98
2. Add file > Upload files.
3. Drag in these items from the unzipped folder: README.md, assets, data, scripts, .gitignore
   (do NOT worry about .github, we do it in Part B).
4. Commit changes.

## Part B: add the 3 bot files (the hidden .github folder)
Windows hides folders that start with a dot, so we create these files by hand.
Do this 3 times, once for each file inside the folder "copy-paste-workflows":
  pixel.yml, scene.yml, snake.yml

1. In your repo click Add file > Create new file.
2. In the file name box type exactly:   .github/workflows/pixel.yml
   (typing the / creates the folders by itself)
3. Open pixel.yml from "copy-paste-workflows" in VS Code, press Ctrl+A, Ctrl+C.
4. Paste into the big GitHub box. Click Commit changes.
5. Repeat with  .github/workflows/scene.yml  and  .github/workflows/snake.yml

## Part C: switch the bots on
1. Settings > Actions > General > Workflow permissions > "Read and write permissions" > Save.
2. Settings > General > Features > tick "Issues".
3. Actions tab > "Update pixel scene" > Run workflow. Wait 1 minute.
4. Actions tab > "Generate contribution snake" > Run workflow. Wait 1 minute.
5. Refresh your profile. Click ADD MY PIXEL yourself to test.
