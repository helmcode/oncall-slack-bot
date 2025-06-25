{{- define "oncall-slack-bot.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "oncall-slack-bot.name" -}}
{{- .Chart.Name -}}
{{- end -}}

{{- define "oncall-slack-bot.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version -}}
{{- end -}}
