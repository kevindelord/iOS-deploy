#!/usr/bin/python
import sys
import argparse
import os
import subprocess
import re

parser = argparse.ArgumentParser(description='Build, archive and push a new iOS app version!')
parser.add_argument('-w','--workspace', help='Path to workspace', required=True, default=None)
parser.add_argument('-s','--scheme', help='Scheme name to build', required=False, default=None)
parser.add_argument('-t','--hockey_api_token', help='Hockey API Token to deliver your app', required=False, default=None)
parser.add_argument('-a','--all_schemes', help='Specify to build all schemes', required=False, default=False, action='store_true')
parser.add_argument('-i','--increment_build', help='Specify to increment the build number', required=False, default=False, action='store_true')
parser.add_argument('-p','--pod_install', help='Specify to run pod install', required=False, default=False, action='store_true')
parser.add_argument('-g','--git_push', help='Specify to commit and push the changes', required=False, default=False, action='store_true')
parser.add_argument('-v','--verbose', help='Specify to log the xcodebuild', required=False, default=False, action='store_true')


args = vars(parser.parse_args())
print args

workspace = args['workspace']

def buildAndPush(project_path, current_workspace, current_scheme):

    print "\n\nNow building scheme: '%s'\n\n" % current_scheme

    if args['hockey_api_token'] != None:
        print "---- Remove previous build files ----"
        os.system('rm -rf %s.xcarchive' % current_scheme)

    print "---- Build .app file ----"
    build_command = 'xcodebuild -workspace %s -scheme %s -configuration "Release" -archivePath %s.xcarchive clean archive' % (current_workspace, current_scheme, current_scheme)
    if args['verbose'] == False: 
        build_command += ' 1>/dev/null'
    print build_command
    os.system(build_command)

    if os.path.exists(project_path + '/' + current_scheme + '.xcarchive') == False:
        print "Archive Failed. Abort deploy process"
        sys.exit()

    if args['hockey_api_token'] != None:
        print "---- Get HockeyAppId ----"
        plist_path = os.popen('xcodebuild -scheme "%s" -configuration "release" -showBuildSettings | grep -e "INFOPLIST_FILE" | sed "s/    INFOPLIST_FILE = //g"' % current_scheme).read().rstrip()
        print "Current target Info.Plist path: '%s'" % plist_path
        hockey_app_id = os.popen('/usr/libexec/PlistBuddy -c Print:HockeyAppId %s' % plist_path).read().rstrip()
        print "Current Target HockeyAppId: '%s'" % hockey_app_id

        print "---- Upload ipa to HockeyApp ----"
        hockey_command = 'puck -submit=auto -download=true -collect_notes_type=jenkins_aggregate -collect_notes_path="." -notes_type=markdown -source_path="."'
        hockey_command += ' -api_token=%s' % args['hockey_api_token']
        hockey_command += ' -app_id=%s' % hockey_app_id
        hockey_command += ' %s.xcarchive' % current_scheme
        print hockey_command
        os.system(hockey_command)

        print "---- Remove current build files ----"
        os.system('rm -rf %s.xcarchive' % current_scheme)

def getAllSchemes():
    # return all schemes
    targets = os.popen('xcodebuild -list -project *.xcodeproj').read().rstrip()
    targets = targets.replace('\n', ' ') # remove all new lines
    targets = targets.replace('\t', ' ') # remove all tabs
    m = re.search('Schemes:(.*?)$', targets)
    if m:
        array = m.group(1).split()
        if len(array) > 0:
            return array
    return []

def getSchemes():
    schemes = []
    # set the sepcified scheme
    if args['scheme'] != None:
        schemes = [args['scheme']]
    # or set ALL targets
    if args['all_schemes'] == True:
        schemes = getAllSchemes()
    elif len(schemes) == 0:
        print "---- List schemes ----"
        os.system('xcodebuild -list -project *.xcodeproj')
        scheme = raw_input("\n\nWhich scheme(s) do you want to build?\nEnter 'ALL_SCHEMES' to build all schemes.\n$> ")
        print "\n\n"
        if scheme == 'ALL_SCHEMES':
            # Get all schemes
            schemes = getAllSchemes()
        elif len(scheme) > 0:
            # Multiple schemes could be specified.
            schemes = scheme.split()

    if len(schemes) == 0:
        print "No scheme specified or found. Abort deploy process"
        sys.exit()
    return schemes

if workspace != None:

    print "---- Jump to project folder ----"
    project_path = workspace + "/.."
    os.chdir(project_path)
    print os.popen('pwd').read().rstrip()

    print "---- Git Pull ----"
    os.system('git pull origin `git symbolic-ref --short -q HEAD`')

    all_schemes = getSchemes()

    if args['increment_build'] == True:
        print "---- Update build version ----"
        os.system('agvtool next-version -all')

    if args['pod_install'] == True:
        print "---- Run Pod install ----"
        os.system('pod install')

    for scheme in all_schemes:
        buildAndPush(project_path, workspace, scheme)    

    if args['git_push'] == True:
        print "---- Git push changes ----"
        os.system('git commit -am "Increment Build Number" ; git push origin `git symbolic-ref --short -q HEAD`')
