# iOS-deploy

```
$> ./deploy.py --help                                                                                                                                                                                     11:59:38
usage: deploy.py [-h] -w WORKSPACE [-s SCHEME] [-t HOCKEY_API_TOKEN] [-a] [-i]
                 [-p] [-g] [-v]

Build, archive and push a new iOS app version!

optional arguments:
  -h, --help            show this help message and exit
  -w WORKSPACE, --workspace WORKSPACE
                        Path to workspace
  -s SCHEME, --scheme SCHEME
                        Scheme name to build
  -t HOCKEY_API_TOKEN, --hockey_api_token HOCKEY_API_TOKEN
                        Hockey API Token to deliver your app
  -a, --all_schemes     Specify to build all schemes
  -i, --increment_build
                        Specify to increment the build number
  -p, --pod_install     Specify to run pod install
  -g, --git_push        Specify to commit and push the changes
  -v, --verbose         Specify to log the xcodebuild
```


The following example will list the schemes for the current workspace, increment the build number, run pod install, deploy the app to hockey and git push to the current branch.
```
./deploy.py -w ~/MyProject/project.xcworkspace -ipg -t API9xxxxxyyyyyyzzzzzz
```

Without the parameter `-t/--hockey_api_token` and a valid token no push to Hockey will occur.
The archives will be created in the same folder as the workspace.