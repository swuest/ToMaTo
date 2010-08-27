# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.http import Http404

from lib import *
import xmlrpclib

def index(request):
	try:
		if not getapi(request):
			return HttpResponseNotAuthorized("Authorization required!")
		api = request.session.api
		return render_to_response("admin/host_index.html", {'host_list': api.host_list()})
	except xmlrpclib.Fault, f:
		return render_to_response("main/error.html", {'error': f})

def add(request):
	try:
		if not request.REQUEST.has_key("hostname"):
			return render_to_response("admin/host_add.html")
		hostname=request.REQUEST["hostname"]
		group=request.REQUEST["group"]
		public_bridge=request.REQUEST["public_bridge"]
		if not getapi(request):
			return HttpResponseNotAuthorized("Authorization required!")
		api = request.session.api
		task_id = api.host_add(hostname, group, public_bridge)
		return render_to_response("admin/host_add.html", {"task_id": task_id, "hostname": hostname})
	except xmlrpclib.Fault, f:
		return render_to_response("main/error.html", {'error': f})

def remove(request, hostname):
	try:
		if not getapi(request):
			return HttpResponseNotAuthorized("Authorization required!")
		api = request.session.api
		api.host_remove(hostname)
		return render_to_response("admin/host_index.html", {'host_list': api.host_list()})
	except xmlrpclib.Fault, f:
		return render_to_response("main/error.html", {'error': f})
