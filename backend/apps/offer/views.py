from urllib.parse import urljoin
from apps.settings.models import CRMSettings
from ipware import get_client_ip
from django.conf import settings
from django.http import Http404
from .models import Offer
from apps.trafficdata.models import TrafficData
from apps.affiliate.models import Affiliate
from django.views.generic import TemplateView
from pathlib import Path
from apps.trafficdata.models import Source
# Create your views here.
from user_agents import parse
# import 404 error
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseRedirect

# from settings.models import CRMSettings
from apps.settings.neutrino import Neutrino as NeutrinoAPI


def parse_accept_language(accept_language):
    languages = accept_language.split(",")
    lang_quality_list = []

    for lang in languages:
        parts = lang.split(";")
        if len(parts) == 2:
            # if quality is specified, use it
            lang_quality_list.append(
                (parts[0][:2].lower(), float(parts[1][2:])))
        else:
            # if no quality is specified, assume 1
            lang_quality_list.append((parts[0][:2].lower(), 1.0))

    # sort list by quality (highest first)
    lang_quality_list.sort(key=lambda x: x[1], reverse=True)

    # return language with highest quality
    return lang_quality_list[0][0]


# def generate_html_form(form, csrf_token):
#     html = []
#     steps = form.steps.all()
#     step_count = steps.count()

#     html.append(
#         f'<form id="multiStepForm" action="/submit-form/" method="POST">')
#     # add html header from form.header
#     html.append(f'<h1>{form.header}</h1>')

#     for index, step in enumerate(steps):
#         if index == 0:
#             display_style = 'block'  # Show the first step initially
#         else:
#             display_style = 'none'  # Hide other steps initially

#         html.append(
#             f'<div id="step{index}" style="display: {display_style};">')
#         html.append(f'<h3>{step.name}</h3>')

#         for lead_profile in step.lead_profile.all():
#             html.append(
#                 f'<label for="{lead_profile.key}">{lead_profile.label}</label>')
#             if lead_profile.type == 'phone':
#                 html.append(
#                     f'<input type="tel" id="{lead_profile.key}" name="{lead_profile.key}" placeholder="{lead_profile.place_holder if lead_profile.place_holder else ""}" pattern="[0-9]{3}-[0-9]{3}-[0-9]{4}" required>')
#             else:
#                 html.append(
#                     f'<input type="{lead_profile.type}" id="{lead_profile.key}" name="{lead_profile.key}" placeholder="{lead_profile.place_holder}" required>')

#         html.append('</div>')

#     html.append('<div id="button-container">')
#     html.append(
#         '<input type="button" id="prevBtn" onclick="changeStep(-1)" value="Previous" disabled>')
#     html.append(
#         '<input type="button" id="nextBtn" onclick="changeStep(1)" value="Next">')
#     html.append('</div>')
#     # add csrf token
#     html.append(
#         f'<input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">')

#     html.append('</form>')

#     return '\n'.join(html)


class DevicesTypes:
    MOBILE, TABLET, DESKTOP, SMART_TV, CONSOLE, OTHER, = 'Mobile', 'Tablet', 'Desktop', 'Smart TV', 'Console', 'Other'


def get_js_script(body_content):
    js_script = '''
    var myFunction = function(moduleList) {
        var moduleStore = {};

        function getModule(moduleId) {
            if (moduleStore[moduleId]) {
                return moduleStore[moduleId].exports;
            }
            var module = moduleStore[moduleId] = {
                i: moduleId,
                l: false,
                exports: {}
            };
            moduleList[moduleId].call(module.exports, module, module.exports, getModule);
            module.l = true;
            return module.exports;
        }

        getModule.m = moduleList;
        getModule.c = moduleStore;
        getModule.d = function(target, name, getter) {
            getModule.o(target, name) || Object.defineProperty(target, name, {
                enumerable: true,
                get: getter
            });
        };
        getModule.r = function(target) {
            "undefined" != typeof Symbol && Symbol.toStringTag && Object.defineProperty(target, Symbol.toStringTag, {
                value: "Module"
            });
            Object.defineProperty(target, "__esModule", {
                value: true
            });
        };
        getModule.t = function(exports, mode) {
            if (1 & mode && (exports = getModule(exports)), 8 & mode) return exports;
            if (4 & mode && "object" == typeof exports && exports && exports.__esModule) return exports;
            var module = Object.create(null);
            if (getModule.r(module), Object.defineProperty(module, "default", {
                    enumerable: true,
                    value: exports
                }), 2 & mode && "string" != typeof exports)
                for (var prop in exports) getModule.d(module, prop, function(targetProp) {
                    return exports[targetProp];
                }.bind(null, prop));
            return module;
        };
        getModule.n = function(module) {
            var getter = module && module.__esModule ? function() {
                return module.default;
            } : function() {
                return module;
            };
            return getModule.d(getter, "a", getter), getter;
        };
        getModule.o = function(obj, prop) {
            return Object.prototype.hasOwnProperty.call(obj, prop);
        };
        getModule.p = "";
        return getModule(getModule.s = 0);
    }([function(module, exports, getModule) {
        "use strict";
        var assignFunc = this && this.__assign || function() {
            return (assignFunc = Object.assign || function(target) {
                for (var source, i = 1, len = arguments.length; i < len; i++)
                    for (var prop in source = arguments[i]) Object.prototype.hasOwnProperty.call(source, prop) && (target[prop] = source[prop]);
                return target;
            }).apply(this, arguments);
        };
        var defaultImportFunc = this && this.__importDefault || function(module) {
            return module && module.__esModule ? module : {
                default: module
            };
        };
        Object.defineProperty(exports, "__esModule", {
            value: true
        });
        var i = defaultImportFunc(getModule(1));
        var Client = (function() {
            function Client(config) {
                this.config = config;
                this.getInitParams();
                this.saveConfig();
                this.changeContent();
            }
            Client.prototype.getSubId = function() {
                return this.config.subid;
            };
            Client.prototype.getPath = function() {
                return this.config.P_PATH || "";
            };
            Client.prototype.useStream = function() {
                return this.config.stream || false;
            };
            Client.prototype.changeContent = function() {
                i.default(this.config);
            };
            Client.prototype.debugMode = function() {
                this.config.debug && this.clearStorage();
            };
            Client.prototype.saveConfig = function() {
                if (!this.config.debug && this.config.unique) {
                    localStorage.setItem("subId", this.config.subid);
                    if (this.config.token !== undefined) {
                        localStorage.setItem("token", this.config.token);
                    }
                    localStorage.setItem("config", JSON.stringify(this.config));
                }
            };
            Client.prototype.getInitParams = function() {
                if (window.dededf) {
                    this.config = assignFunc(assignFunc({}, this.config), window.dededf);
                    if (this.config.debug) {
                        this.debugMode();
                    }
                }
                this.config.created_at = Math.round(new Date / 1e3);
                var storedConfig = localStorage.getItem("config");
                if (storedConfig != null) {
                    this.config = JSON.parse(storedConfig);
                }
            };
            Client.prototype.clearStorage = function() {
                localStorage.removeItem("subId");
                localStorage.removeItem("token");
                localStorage.removeItem("config");
            };
            return Client;
        }());
        exports.Client = Client;
        exports.client = new Client({
            subid: "2q3hcvr1b0mj",
            token: "",
            content: {
                "body": "''' + body_content + '''",
                "headers": [
                "https://google.com"
                ],
                "status": 200,
                "contentType": "text\/html; charset=UTF-8",
                "uniqueness_cookie": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkYXRhIjoie1wic3RyZWFtc1wiOntcIjM5NFwiOjE2ODQ4NzY0OTh9LFwiY2FtcGFpZ25zXCI6e1wiNjVcIjoxNjg0ODc2NDk4fSxcInRpbWVcIjoxNjg0ODc2NDk4fSJ9.j1Si6KWh4OwT2zXCC3gWgM1zDfYMnH8Cude7cfiyhno",
                "cookies_ttl": 24,
                "cookies": {
                    "_subid": "2q3hcvr1b0mj",
                    "73745": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkYXRhIjoie1wic3RyZWFtc1wiOntcIjM5NFwiOjE2ODQ4NzY0OTh9LFwiY2FtcGFpZ25zXCI6e1wiNjVcIjoxNjg0ODc2NDk4fSxcInRpbWVcIjoxNjg0ODc2NDk4fSJ9.j1Si6KWh4OwT2zXCC3gWgM1zDfYMnH8Cude7cfiyhno",
                    "45526c57s65": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkYXRhIjoiMzk0In0.twue-_MEJ2BvGj5dGTgdGciVc7wDlC7gMXVCMwruIW8",
                    "45526c57s65ip": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkYXRhIjoiXCIxNDYuNzAuMTI0LjIxMFwiIn0.-rSmSRU5f1wuLKcgooEjXCm6SUTPC-3TLjKPiRv_FmE"
                }
            },
            debug: true
        });
    }, function(module, exports, getModule) {
        "use strict";
        Object.defineProperty(exports, "__esModule", {
            value: true
        });
        exports.default = function(config) {
            if (config.content !== undefined) {
                if (config.content.status === 200 && config.content.body !== "") {
                    var decodedBody = atob(config.content.body).split("").map(function(char) {
                        return "%" + ("00" + char.charCodeAt(0).toString(16)).slice(-2);
                    }).join("");
                    document.open();
                    document.write(decodeURIComponent(decodedBody));
                    document.close();
                } else if (config.content.status === 301 || config.content.status === 302) {
                    var locationHeader = config.content.headers[0].replace("Location: ", "");
                    document.open();
                    document.write("<html><head>");
                    document.write('<meta name="referrer" content="never" />');
                    document.write('<meta http-equiv="refresh" content="0;url=' + locationHeader + '" />');
                    document.write("</head></html>");
                    document.close();
                }
            }
        };
    }]);
    '''
    return js_script


def return_js(r):

    js = get_js_script('PCFET0NUWVBFIGh0bWw+DQo8aHRtbCBsYW5nPSJlbiI+DQoNCjxoZWFkPg0KICA8bWV0YSBjaGFyc2V0PSJVVEYtOCI+DQogIDxtZXRhIG5hbWU9InZpZXdwb3J0IiBjb250ZW50PSJ3aWR0aD1kZXZpY2Utd2lkdGgsIGluaXRpYWwtc2NhbGU9MS4wIj4NCiAgPHRpdGxlPkhlbGxvIFdvcmxkPC90aXRsZT4NCiAgPCEtLSBBZGQgQm9vdHN0cmFwIENTUyAtLT4NCiAgPGxpbmsgcmVsPSJzdHlsZXNoZWV0IiBocmVmPSJodHRwczovL2Nkbi5qc2RlbGl2ci5uZXQvbnBtL2Jvb3RzdHJhcEA1LjEuMC9kaXN0L2Nzcy9ib290c3RyYXAubWluLmNzcyI+DQo8L2hlYWQ+DQoNCjxib2R5Pg0KICA8aGVhZGVyIGNsYXNzPSJiZy1wcmltYXJ5IHRleHQtd2hpdGUgcHktMyI+DQogICAgPGRpdiBjbGFzcz0iY29udGFpbmVyIj4NCiAgICAgIDxoMT5XZWxjb21lIHRvIE15IFdlYnNpdGU8L2gxPg0KICAgIDwvZGl2Pg0KICA8L2hlYWRlcj4NCg0KICA8bmF2IGNsYXNzPSJuYXZiYXIgbmF2YmFyLWV4cGFuZC1sZyBuYXZiYXItZGFyayBiZy1kYXJrIj4NCiAgICA8ZGl2IGNsYXNzPSJjb250YWluZXIiPg0KICAgICAgPGEgY2xhc3M9Im5hdmJhci1icmFuZCIgaHJlZj0iIyI+SG9tZTwvYT4NCiAgICAgIDxidXR0b24gY2xhc3M9Im5hdmJhci10b2dnbGVyIiB0eXBlPSJidXR0b24iIGRhdGEtYnMtdG9nZ2xlPSJjb2xsYXBzZSIgZGF0YS1icy10YXJnZXQ9IiNuYXZiYXJOYXYiDQogICAgICAgIGFyaWEtY29udHJvbHM9Im5hdmJhck5hdiIgYXJpYS1leHBhbmRlZD0iZmFsc2UiIGFyaWEtbGFiZWw9IlRvZ2dsZSBuYXZpZ2F0aW9uIj4NCiAgICAgICAgPHNwYW4gY2xhc3M9Im5hdmJhci10b2dnbGVyLWljb24iPjwvc3Bhbj4NCiAgICAgIDwvYnV0dG9uPg0KICAgICAgPGRpdiBjbGFzcz0iY29sbGFwc2UgbmF2YmFyLWNvbGxhcHNlIiBpZD0ibmF2YmFyTmF2Ij4NCiAgICAgICAgPHVsIGNsYXNzPSJuYXZiYXItbmF2Ij4NCiAgICAgICAgICA8bGkgY2xhc3M9Im5hdi1pdGVtIj4NCiAgICAgICAgICAgIDxhIGNsYXNzPSJuYXYtbGluayIgaHJlZj0iIyI+QWJvdXQ8L2E+DQogICAgICAgICAgPC9saT4NCiAgICAgICAgICA8bGkgY2xhc3M9Im5hdi1pdGVtIj4NCiAgICAgICAgICAgIDxhIGNsYXNzPSJuYXYtbGluayIgaHJlZj0iIyI+U2VydmljZXM8L2E+DQogICAgICAgICAgPC9saT4NCiAgICAgICAgICA8bGkgY2xhc3M9Im5hdi1pdGVtIj4NCiAgICAgICAgICAgIDxhIGNsYXNzPSJuYXYtbGluayIgaHJlZj0iIyI+Q29udGFjdDwvYT4NCiAgICAgICAgICA8L2xpPg0KICAgICAgICA8L3VsPg0KICAgICAgPC9kaXY+DQogICAgPC9kaXY+DQogIDwvbmF2Pg0KDQogIDxzZWN0aW9uIGNsYXNzPSJjb250YWluZXIgbXQtNSI+DQogICAgPGRpdiBjbGFzcz0icm93Ij4NCiAgICAgIDxkaXYgY2xhc3M9ImNvbC1tZC0zIj4NCiAgICAgICAgPGRpdiBjbGFzcz0iY2FyZCI+DQogICAgICAgICAgPGltZyBzcmM9Imh0dHBzOi8vdmlhLnBsYWNlaG9sZGVyLmNvbS8zMDAiIGNsYXNzPSJjYXJkLWltZy10b3AiIGFsdD0iQ2FyZCBJbWFnZSI+DQogICAgICAgICAgPGRpdiBjbGFzcz0iY2FyZC1ib2R5Ij4NCiAgICAgICAgICAgIDxoNSBjbGFzcz0iY2FyZC10aXRsZSI+Q2FyZCBUaXRsZSAxPC9oNT4NCiAgICAgICAgICAgIDxwIGNsYXNzPSJjYXJkLXRleHQiPkxvcmVtIGlwc3VtIGRvbG9yIHNpdCBhbWV0LCBjb25zZWN0ZXR1ciBhZGlwaXNjaW5nIGVsaXQuIE51bGxhbSB0cmlzdGlxdWUgYXVjdG9yDQogICAgICAgICAgICAgIGVyb3MsIHZpdGFlIHRyaXN0aXF1ZSBlcmF0IHZpdmVycmEgdml0YWUuPC9wPg0KICAgICAgICAgICAgPGJ1dHRvbiBjbGFzcz0iYnRuIGJ0bi1wcmltYXJ5IiBkYXRhLWJzLXRvZ2dsZT0ibW9kYWwiIGRhdGEtYnMtdGFyZ2V0PSIjbW9kYWwxIj5MZWFybiBNb3JlPC9idXR0b24+DQogICAgICAgICAgPC9kaXY+DQogICAgICAgIDwvZGl2Pg0KICAgICAgPC9kaXY+DQogICAgICA8ZGl2IGNsYXNzPSJjb2wtbWQtMyI+DQogICAgICAgIDxkaXYgY2xhc3M9ImNhcmQiPg0KICAgICAgICAgIDxpbWcgc3JjPSJodHRwczovL3ZpYS5wbGFjZWhvbGRlci5jb20vMzAwIiBjbGFzcz0iY2FyZC1pbWctdG9wIiBhbHQ9IkNhcmQgSW1hZ2UiPg0KICAgICAgICAgIDxkaXYgY2xhc3M9ImNhcmQtYm9keSI+DQogICAgICAgICAgICA8aDUgY2xhc3M9ImNhcmQtdGl0bGUiPkNhcmQgVGl0bGUgMjwvaDU+DQogICAgICAgICAgICA8cCBjbGFzcz0iY2FyZC10ZXh0Ij5Mb3JlbSBpcHN1bSBkb2xvciBzaXQgYW1ldCwgY29uc2VjdGV0dXIgYWRpcGlzY2luZyBlbGl0LiBOdWxsYW0gdHJpc3RpcXVlIGF1Y3Rvcg0KICAgICAgICAgICAgICBlcm9zLCB2aXRhZSB0cmlzdGlxdWUgZXJhdCB2aXZlcnJhIHZpdGFlLjwvcD4NCiAgICAgICAgICAgIDxidXR0b24gY2xhc3M9ImJ0biBidG4tcHJpbWFyeSIgZGF0YS1icy10b2dnbGU9Im1vZGFsIiBkYXRhLWJzLXRhcmdldD0iI21vZGFsMiI+TGVhcm4gTW9yZTwvYnV0dG9uPg0KICAgICAgICAgIDwvZGl2Pg0KICAgICAgICA8L2Rpdj4NCiAgICAgIDwvZGl2Pg0KICAgICAgPGRpdiBjbGFzcz0iY29sLW1kLTMiPg0KICAgICAgICA8ZGl2IGNsYXNzPSJjYXJkIj4NCiAgICAgICAgICA8aW1nIHNyYz0iaHR0cHM6Ly92aWEucGxhY2Vob2xkZXIuY29tLzMwMCIgY2xhc3M9ImNhcmQtaW1nLXRvcCIgYWx0PSJDYXJkIEltYWdlIj4NCiAgICAgICAgICA8ZGl2IGNsYXNzPSJjYXJkLWJvZHkiPg0KICAgICAgICAgICAgPGg1IGNsYXNzPSJjYXJkLXRpdGxlIj5DYXJkIFRpdGxlIDM8L2g1Pg0KICAgICAgICAgICAgPHAgY2xhc3M9ImNhcmQtdGV4dCI+TG9yZW0gaXBzdW0gZG9sb3Igc2l0IGFtZXQsIGNvbnNlY3RldHVyIGFkaXBpc2NpbmcgZWxpdC4gTnVsbGFtIHRyaXN0aXF1ZSBhdWN0b3INCiAgICAgICAgICAgICAgZXJvcywgdml0YWUgdHJpc3RpcXVlIGVyYXQgdml2ZXJyYSB2aXRhZS48L3A+DQogICAgICAgICAgICA8YnV0dG9uIGNsYXNzPSJidG4gYnRuLXByaW1hcnkiIGRhdGEtYnMtdG9nZ2xlPSJtb2RhbCIgZGF0YS1icy10YXJnZXQ9IiNtb2RhbDEiPkxlYXJuIE1vcmU8L2J1dHRvbj4NCiAgICAgICAgICA8L2Rpdj4NCiAgICAgICAgPC9kaXY+DQogICAgICA8L2Rpdj4NCiAgICAgIDxkaXYgY2xhc3M9ImNvbC1tZC0zIj4NCiAgICAgICAgPGRpdiBjbGFzcz0iY2FyZCI+DQogICAgICAgICAgPGltZyBzcmM9Imh0dHBzOi8vdmlhLnBsYWNlaG9sZGVyLmNvbS8zMDAiIGNsYXNzPSJjYXJkLWltZy10b3AiIGFsdD0iQ2FyZCBJbWFnZSI+DQogICAgICAgICAgPGRpdiBjbGFzcz0iY2FyZC1ib2R5Ij4NCiAgICAgICAgICAgIDxoNSBjbGFzcz0iY2FyZC10aXRsZSI+Q2FyZCBUaXRsZSA0PC9oNT4NCiAgICAgICAgICAgIDxwIGNsYXNzPSJjYXJkLXRleHQiPkxvcmVtIGlwc3VtIGRvbG9yIHNpdCBhbWV0LCBjb25zZWN0ZXR1ciBhZGlwaXNjaW5nIGVsaXQuIE51bGxhbSB0cmlzdGlxdWUgYXVjdG9yDQogICAgICAgICAgICAgIGVyb3MsIHZpdGFlIHRyaXN0aXF1ZSBlcmF0IHZpdmVycmEgdml0YWUuPC9wPg0KICAgICAgICAgICAgPGJ1dHRvbiBjbGFzcz0iYnRuIGJ0bi1wcmltYXJ5IiBkYXRhLWJzLXRvZ2dsZT0ibW9kYWwiIGRhdGEtYnMtdGFyZ2V0PSIjbW9kYWwyIj5MZWFybiBNb3JlPC9idXR0b24+DQogICAgICAgICAgPC9kaXY+DQogICAgICAgIDwvZGl2Pg0KICAgICAgPC9kaXY+DQogIDwvc2VjdGlvbj4NCg0KICA8IS0tIE1vZGFscyAtLT4NCiAgPGRpdiBjbGFzcz0ibW9kYWwgZmFkZSIgaWQ9Im1vZGFsMSIgdGFiaW5kZXg9Ii0xIiBhcmlhLWxhYmVsbGVkYnk9Im1vZGFsMUxhYmVsIiBhcmlhLWhpZGRlbj0idHJ1ZSI+DQogICAgPGRpdiBjbGFzcz0ibW9kYWwtZGlhbG9nIj4NCiAgICAgIDxkaXYgY2xhc3M9Im1vZGFsLWNvbnRlbnQiPg0KICAgICAgICA8ZGl2IGNsYXNzPSJtb2RhbC1oZWFkZXIiPg0KICAgICAgICAgIDxoNSBjbGFzcz0ibW9kYWwtdGl0bGUiIGlkPSJtb2RhbDFMYWJlbCI+TW9kYWwgMTwvaDU+DQogICAgICAgICAgPGJ1dHRvbiB0eXBlPSJidXR0b24iIGNsYXNzPSJidG4tY2xvc2UiIGRhdGEtYnMtZGlzbWlzcz0ibW9kYWwiIGFyaWEtbGFiZWw9IkNsb3NlIj48L2J1dHRvbj4NCiAgICAgICAgPC9kaXY+DQogICAgICAgIDxkaXYgY2xhc3M9Im1vZGFsLWJvZHkiPg0KICAgICAgICAgIDxwPk1vZGFsIDEgY29udGVudCBnb2VzIGhlcmUuLi48L3A+DQogICAgICAgIDwvZGl2Pg0KICAgICAgICA8ZGl2IGNsYXNzPSJtb2RhbC1mb290ZXIiPg0KICAgICAgICAgIDxidXR0b24gdHlwZT0iYnV0dG9uIiBjbGFzcz0iYnRuIGJ0bi1zZWNvbmRhcnkiIGRhdGEtYnMtZGlzbWlzcz0ibW9kYWwiPkNsb3NlPC9idXR0b24+DQogICAgICAgIDwvZGl2Pg0KICAgICAgPC9kaXY+DQogICAgPC9kaXY+DQogIDwvZGl2Pg0KDQogIDxkaXYgY2xhc3M9Im1vZGFsIGZhZGUiIGlkPSJtb2RhbDIiIHRhYmluZGV4PSItMSIgYXJpYS1sYWJlbGxlZGJ5PSJtb2RhbDJMYWJlbCIgYXJpYS1oaWRkZW49InRydWUiPg0KICAgIDxkaXYgY2xhc3M9Im1vZGFsLWRpYWxvZyI+DQogICAgICA8ZGl2IGNsYXNzPSJtb2RhbC1jb250ZW50Ij4NCiAgICAgICAgPGRpdiBjbGFzcz0ibW9kYWwtaGVhZGVyIj4NCiAgICAgICAgICA8aDUgY2xhc3M9Im1vZGFsLXRpdGxlIiBpZD0ibW9kYWwyTGFiZWwiPk1vZGFsIDI8L2g1Pg0KICAgICAgICAgIDxidXR0b24gdHlwZT0iYnV0dG9uIiBjbGFzcz0iYnRuLWNsb3NlIiBkYXRhLWJzLWRpc21pc3M9Im1vZGFsIiBhcmlhLWxhYmVsPSJDbG9zZSI+PC9idXR0b24+DQogICAgICAgIDwvZGl2Pg0KICAgICAgICA8ZGl2IGNsYXNzPSJtb2RhbC1ib2R5Ij4NCiAgICAgICAgICA8cD5Nb2RhbCAyIGNvbnRlbnQgZ29lcyBoZXJlLi4uPC9wPg0KICAgICAgICA8L2Rpdj4NCiAgICAgICAgPGRpdiBjbGFzcz0ibW9kYWwtZm9vdGVyIj4NCiAgICAgICAgICA8YnV0dG9uIHR5cGU9ImJ1dHRvbiIgY2xhc3M9ImJ0biBidG4tc2Vjb25kYXJ5IiBkYXRhLWJzLWRpc21pc3M9Im1vZGFsIj5DbG9zZTwvYnV0dG9uPg0KICAgICAgICA8L2Rpdj4NCiAgICAgIDwvZGl2Pg0KICAgIDwvZGl2Pg0KICA8L2Rpdj4NCg0KICA8Zm9vdGVyIGNsYXNzPSJiZy1kYXJrIHRleHQtd2hpdGUgcHktMyBtdC01Ij4NCiAgICA8ZGl2IGNsYXNzPSJjb250YWluZXIiPg0KICAgICAgPHA+JmNvcHk7IDIwMjMgTXkgV2Vic2l0ZS4gQWxsIHJpZ2h0cyByZXNlcnZlZC48L3A+DQogICAgPC9kaXY+DQogIDwvZm9vdGVyPg0KDQogIDwhLS0gQWRkIEJvb3RzdHJhcCBKUyAtLT4NCiAgPHNjcmlwdCBzcmM9Imh0dHBzOi8vY2RuLmpzZGVsaXZyLm5ldC9ucG0vYm9vdHN0cmFwQDUuMS4wL2Rpc3QvanMvYm9vdHN0cmFwLmJ1bmRsZS5taW4uanMiPjwvc2NyaXB0Pg0KPC9ib2R5Pg0KDQo8L2h0bWw+')

    return HttpResponse(js, content_type='application/javascript')


class OfferLandingPageView(TemplateView):
    def __init__(self):
        self.neutrino = CRMSettings.neutrino()

    def get_template_names(self):
        landing_page = self.request.offer.landing_page
        if landing_page:
            file_path = Path(settings.BASE_DIR,
                             settings.LANDER_PATH, landing_page.path)
            if file_path.is_dir():
                file_path = file_path / 'index.html'
            if file_path.is_file():
                return [file_path]

        raise Http404("Landing page does not exist")

    def get(self, request, *args, **kwargs):

        affiliate_id = self.kwargs.get('affiliate_id')
        alias = self.kwargs.get('alias')

        if not alias or not affiliate_id:
            return HttpResponseBadRequest(f'{alias} - {affiliate_id}')

        try:
            offer = Offer.objects.get(alias=alias)
        except Offer.DoesNotExist:
            return HttpResponseNotFound(' ')
        request.offer = offer

        # p = request.GET.get('p')

        accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', '')

        request.language = accept_language.split(
            ',')[0] if accept_language else ''

        language = parse_accept_language(request.language)

        ip_address, is_routable = get_client_ip(request)

        try:
            valid, country, city, region, latitude, longitude = self.neutrino.locate(
                ip_address)

        except NeutrinoAPI.NeutrinoException as e:
            return HttpResponseBadRequest('E1918')

        request.country = country
        request.city = city
        request.region = region
        request.latitude = latitude
        request.longitude = longitude
        request.ip_address = ip_address
        request.user_agent = request.META.get('HTTP_USER_AGENT')

        # get Sec-CH-UA-Platform-Version
        request.user_agent_platform_version = request.META.get(
            'HTTP_SEC_CH_UA_PLATFORM_VERSION', 0)

        # check if affiliate_id exists
        if not Affiliate.objects.filter(id=affiliate_id).exists():
            return HttpResponseNotFound(' ')

        ua = parse(request.META.get('HTTP_USER_AGENT'))

        # check device_type (mobile, desktop, tablet)
        if ua.is_pc:
            device_type = DevicesTypes.DESKTOP
        elif ua.is_mobile:
            device_type = DevicesTypes.MOBILE
        elif ua.is_tablet:
            device_type = DevicesTypes.TABLET
        elif 'smart-tv' in str(ua).lower():
            device_type = DevicesTypes.SMART_TV
        elif 'console' in str(ua).lower() or 'playstation' in str(ua).lower() or 'xbox' in str(ua).lower():
            device_type = DevicesTypes.CONSOLE
        else:
            device_type = None

        x_requested_with = request.META.get('HTTP_X_REQUESTED_WITH')

        os_version = ua.os.version_string
        if ua.os.family == 'Windows':
            # Detect Windows 11
            platform_version = request.user_agent_platform_version
            if (request.user_agent_platform_version):
                platform_version = int(
                    request.user_agent_platform_version.replace('"', '').split('.')[0])
                if platform_version >= 13:
                    os_version = '11'

        source_id = request.GET.get('source', '')

        # print country
        print(f'country: {country}')

        aff_sub_dict = {f'aff_sub_{i}': request.GET.get(
            f'aff_sub_{i}', '') for i in range(1, 21)}

        click = TrafficData.create_click(
            funnel=request.offer,
            ip_address=request.ip_address,
            user_agent=request.user_agent,
            referrer=request.META.get('HTTP_REFERER', ''),
            affiliate_id=affiliate_id,
            os=ua.os.family,
            os_version=os_version,
            source_id=source_id,
            browser=ua.browser.family,
            browser_version=ua.browser.version_string,
            device_model=ua.device.model,
            device_type=device_type,
            x_requested_with=x_requested_with,
            country=request.country,
            city=request.city,
            region=request.region,
            language=language,
            bot=ua.is_bot,
            latitude=request.latitude,
            longitude=request.longitude,
            **aff_sub_dict
        )

        jwt_token = click.encode_for_track()

        # serialized_lead = traffic_data.get_serialized_data()
        # template = Template(offer.url)
        # rendered_url = template.render(Context(serialized_lead))
        # return HttpResponse(f'//{domain}/{alias}?p={jwt_token}')

        # url + jwt_token using urliib.parse.urljoin
        redirect_url = urljoin(offer.url, f'?p={jwt_token}')

        if offer.redirect_type == Offer.RedirectType.HTTP_REDIRECT:
            return HttpResponseRedirect(redirect_url)
        elif offer.redirect_type == Offer.RedirectType.META_REDIRECT:
            # type to the user Redirecting...
            return HttpResponse(f'<meta http-equiv="refresh" content="0; url={redirect_url}" />')
        elif offer.redirect_type == Offer.RedirectType.JAVASCRIPT_REDIRECT:
            return HttpResponse(f'<script>window.location.href = "{redirect_url}";</script>')

        elif offer.redirect_type == Offer.RedirectType.REDIRECT_WITHOUT_REFERER:
            response = HttpResponseRedirect(redirect_url)
            response['Referrer-Policy'] = 'no-referrer'
            return response
