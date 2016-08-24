# Create your views here.
# coding: utf8

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
        c = MySQLdb.connect(host='localhost', user='cmdb', passwd='cmdb', db='cmdb', port=3306, charset='utf8')
        cur = c.cursor()
        sql = "select  d.name from auth_group as d,(select a.group_id from auth_user_groups as a,(select id from auth_user where username = '%s') as b where a.user_id = b.id) as c where d.id = c.group_id ; " % username
        cur.execute(sql)
        t = cur.fetchall()
        cur.close()
        c.close()
        a = []
        for i in t:
            a.append(i[0])
        return a
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

        if group[0] == 'admin':
            return HttpResponseRedirect('/update/')
        else:
            return HttpResponseRedirect('/program/')

    else:
        return render_to_response('error.html')


@login_required(login_url="")
def weblogout(request):
    logout(request)
    return render_to_response("index.html")


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
    name = project_info()  # 所有项目字典
    username = request.user.username
    group = mysqlgroup(username)  # 用户所属组的列表
    id_list = dictkey(group, name)  # 用户对应的 id列表
    if request.method == 'POST':
        one = request.POST['one']
        two = request.POST['two']
        projectid = request.POST['three']
        if group[0] == 'admin':
            projectname = name  # select遍历
        else:
            projectname = filter_grouplist(id_list, name)  # 普通用户的 select遍历

        labels, dataline = project_costline(one, two, projectid)
        end = 1000000
        scale = 200000
        projectid = int(projectid)
        project_name = name[projectid]       # 下标 项目名

    else:
        one = '2016-01-01'
        two = '2016-09-01'
        if group[0] == 'admin':
            projectid = 1000330
            projectname = name
        else:
            projectid = id_list[0]
            projectid = int(projectid)
            projectname = filter_grouplist(id_list, name)
        labels, dataline = project_costline(one, two, projectid)
        end = 1000000
        scale = 200000
        project_name = name[projectid]
    print group
    print projectname
    return render_to_response('line.html',
                              {'flow': json.dumps(dataline), 'labels': json.dumps(labels), 'end': json.dumps(end),
                               'scale': json.dumps(scale),
                               'one': one, 'two': two, 'projectname': projectname, 'program': json.dumps(project_name),
                               'projectid': projectid})


@login_required(login_url="")
def table(request):
    name = project_info()
    username = request.user.username
    group = mysqlgroup(username)
    id_list = dictkey(group, name)
    if request.method == 'POST':
        one = request.POST['one']
        two = request.POST['two']
        projectid = request.POST['three']
        if group[0] == 'admin':
            projectname = name
        else:
            projectname = filter_grouplist(id_list, name)
        fee = project_costtable(one, two, projectid)
        projectid = int(projectid)
        project_name = name[projectid]
    else:
        one = '2016-01-01'
        two = '2016-09-01'
        if group[0] == 'admin':
            projectid = 1000330
            projectname = name
        else:
            projectid = id_list[0]
            projectid = int(projectid)
            projectname = filter_grouplist(id_list, name)
        fee = project_costtable(one, two, projectid)
        project_name = name[projectid]
    return render_to_response('table.html',
                              {'dat': fee, 'program': project_name, 'one': one, 'two': two, 'projectid': projectid,
                               'projectname': projectname})


@login_required(login_url="")
def information(request):
    name = project_info()
    username = request.user.username
    group = mysqlgroup(username)
    id_list = dictkey(group, name)
    if group[0] == 'admin':
        projectname = name
        if request.method == 'POST':
            projectid = request.POST['three']
        else:
            projectid = 1000330
        project_name = name[projectid]
    else:
        if request.method == 'POST':
            projectid = request.POST['three']
        else:
            projectid = id_list[0]
        projectid = int(projectid)
        project_name = name[projectid]
        projectname = filter_grouplist(id_list, name)
    return render_to_response('information.html',
                              {'projectname': projectname, 'program': project_name, 'projectid': projectid})


def dictkey(i, d):
    a = []
    for j in i:
        for k, v in d.items():
            if v == j:
                a.append(k)
    return a


def filter_grouplist(l, d):
    a = {}
    for i in l:
        a[i] = d[i]
    return a

@login_required(login_url="")
def program(request):
    username = request.user.username
    group = mysqlgroup(username)
    name = project_info()
    id_list = dictkey(group, name)
    projectname = filter_grouplist(id_list, name)
    print username
    print group

    if request.method == 'POST':
        one = request.POST['one']
        two = request.POST['two']
        projectid = request.POST['three']
    else:
        one = '2016-01-01'
        two = '2016-09-01'
        projectid = id_list[0]
    projectid = int(projectid)
    groupname = name[int(projectid)]
    data = project_cost(one, two, projectid)
    print data
    print projectname
    print projectid
    return render_to_response('program.html',
                              {'cost': json.dumps(data), 'username': username, 'program': group, 'one': one,
                               'two': two, 'projectname': projectname, 'groupname': json.dumps(groupname), 'projectid':projectid})
