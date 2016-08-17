# Create your views here.
from django.shortcuts import render, render_to_response, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

import MySQLdb
from MySQLdb.constants import FIELD_TYPE
import json
import sys


def mysqlgroup(username):
    try:
        c = MySQLdb.connect(host='localhost', user='cmdb', passwd='cmdb', db='cmdb', port=3306)
        cur = c.cursor()
        sql = 'select c.name from auth_user as a,auth_user_groups as b,auth_group as c where a.id=b.user_id and b.group_id = c.id and a.username="%s";' % username
        cur.execute(sql)
        t = cur.fetchall()
        cur.close()
        c.close()
        return t[0][0]
    except Exception, e:
        print e


def mysqlselect(sql):
    my_conv = {FIELD_TYPE.TIMESTAMP: str}
    conn = MySQLdb.connect(host="localhost", user="ledou", passwd="ledou", db="ledou_cmdb", port=3306,
                           conv=my_conv)
    cur = conn.cursor()
    cur.execute('set names utf8')
    cur.execute(sql)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data


def project_info():
    conn = MySQLdb.connect(host="localhost", user="ledou", passwd="ledou", db="ledou_cmdb", port=3306, charset='utf8')
    cur = conn.cursor()
    sql = 'select projectid,projectName from project_info;'
    cur.execute('set names utf8')
    cur.execute(sql)
    name = cur.fetchall()
    cur.close()
    conn.close()
    data = []
    for i in name:
        d = []
        d.append(int(i[0]))
        d.append(i[1])
        data.append(d)
    project_dict = []
    for i in data:
        project_dict.append(tuple(i))
    name = dict(project_dict)
    return name


def test(request):
    name = project_info()
    return render_to_response('bar.html', {'projectname': name})


def project_cost(on, tw, projectid):
    one = on.replace('-', '', 2)
    two = tw.replace('-', '', 2)
    sql = 'select date,money from server_costs where date between "%s" and "%s" and projectId = %s;' % (
    one, two, projectid)
    t = mysqlselect(sql)
    d = []
    l = []
    for i in t:
        d.append(str(i[0]))
        l.append(int(i[1]))
    b = []
    for i in range(20):
        b.append('#32bdbc')

    z = zip(d, l, b)

    a = []
    for i in z:
        a.append({'name': i[0], 'value': int(i[1]), 'color': i[2]})

    return a


def project_costline(on, tw, projectid):
    one = on.replace('-', '', 2)
    two = tw.replace('-', '', 2)
    sql = 'select date,money from server_costs where date between "%s" and "%s" and projectId = %s;' % (
    one, two, projectid)
    t = mysqlselect(sql)
    d = []
    l = []
    for i in t:
        d.append(str(i[0]))
        l.append(int(i[1]))

    return d, l


def project_costtable(on, tw, projectid):
    one = on.replace('-', '', 2)
    two = tw.replace('-', '', 2)
    sql = 'select date,money from server_costs where date between "%s" and "%s" and projectId = %s;' % (
    one, two, projectid)
    t = mysqlselect(sql)
    d = []
    l = []
    for i in t:
        d.append(str(i[0]))
        l.append(int(i[1]))
    b = []
    for i in range(20):
        b.append('#32bdbc')

    z = zip(d, l, b)
    print z

    a = []
    for i in z:
        a.append({'name': i[0], 'value': int(i[1]), 'color': i[2]})

    return a


def index(request):
    return render_to_response('index.html')


def weblogin(request):
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user is not None:
        login(request, user)
        username = user.username
        group = mysqlgroup(username)

        if group == 'admin':
            return HttpResponseRedirect('/update/')
        else:
            return HttpResponseRedirect('/baruser/')

    else:
        return render_to_response('error.html')


@login_required(login_url="")
def weblogout(request):
    logout(request)
    return  render_to_response("index.html")


@login_required(login_url="")
def update(request):
    name = project_info()
    end = 1000000
    scale = 100000
    username = request.user.username
    if request.method == 'POST':
        one = request.POST['one']
        two = request.POST['two']
        projectid = request.POST['three']
        data = project_cost(one, two, projectid)
        t = int(projectid)
        project_name = name[t]
        projectid = t
    else:
        one = '2016-01-01'
        two = '2016-09-01'
        projectid = '1000330'
        data = project_cost(one, two, projectid)
        t = int(projectid)
        project_name = name[t]
        projectid = t
    return render_to_response('bar.html',
                              {'cost': json.dumps(data), 'projectid': projectid, 'end': json.dumps(end),
                               'scale': json.dumps(scale),
                               'username': username, 'one': one, 'two': two, 'projectname': name,
                               'program': json.dumps(project_name)})

@login_required(login_url="")
def line(request):
    name = project_info()
    if request.method == 'POST':
        one = request.POST['one']
        two = request.POST['two']
        projectid = request.POST['three']
        labels, dataline = project_costline(one, two, projectid)
        end = 1000000
        scale = 200000
        t = int(projectid)
        project_name = name[t]
        projectid = t

    else:
        one = '2016-01-01'
        two = '2016-09-01'
        projectid = '1000330'
        labels, dataline = project_costline(one, two, projectid)
        print labels
        print dataline
        end = 1000000
        scale = 200000
        t = 1000330
        project_name = name[t]
        projectid = t

    return render_to_response('line.html',
                              {'flow': json.dumps(dataline), 'labels': json.dumps(labels), 'end': json.dumps(end),
                               'scale': json.dumps(scale),
                               'one': one, 'two': two, 'projectname': name, 'program': json.dumps(project_name),
                               'projectid': projectid})

@login_required(login_url="")
def table(request):
    name = project_info()
    if request.method == 'POST':
        one = request.POST['one']
        two = request.POST['two']
        projectid = request.POST['three']
        fee = project_costtable(one, two, projectid)
        t = int(projectid)
        project_name = name[t]
        projectid = t
    else:
        one = '2016-01-01'
        two = '2016-09-01'
        projectid = '1000330'
        fee = project_costtable(one, two, projectid)
        t = 1000330
        project_name = name[t]
        projectid = t
    return render_to_response('table.html', {'dat': fee, 'program': project_name, 'one': one, 'two': two, 'projectid': projectid, 'projectname': name})

@login_required(login_url="")
def information(request):
    return render_to_response('information.html')