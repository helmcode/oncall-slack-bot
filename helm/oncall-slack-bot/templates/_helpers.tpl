{{/*
Devuelve el nombre completo del recurso: simplemente el nombre del release
Ej: "oncall-slack-bot"
*/}}
{{- define "oncall-slack-bot.fullname" -}}
{{ .Release.Name }}
{{- end -}}

{{/*
Nombre del chart
Ej: "oncall-slack-bot"
*/}}
{{- define "oncall-slack-bot.name" -}}
{{- .Chart.Name -}}
{{- end -}}

{{/*
Versión del chart (útil para etiquetas)
Ej: "oncall-slack-bot-0.1.0"
*/}}
{{- define "oncall-slack-bot.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version -}}
{{- end -}}

{{/*
Nombre del Secret de Postgres (o cualquier secreto sensible)
Ej: "oncall-slack-bot-pg-secret"
*/}}
{{- define "oncall-slack-bot.secretName" -}}
{{- printf "%s-pg-secret" (include "oncall-slack-bot.fullname" .) -}}
{{- end -}}