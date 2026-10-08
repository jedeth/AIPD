# Surcharges propres au déploiement conteneurisé (monté en lecture seule dans
# config/initializers/ : le dépôt pia-back n'est pas modifié).

# --- HTTPS -----------------------------------------------------------------
# production.rb force le SSL. Tant que l'accès se fait en HTTP (tunnel SSH),
# PIA_FORCE_SSL=false le désactive. Mettre true derrière un vrai HTTPS.
force_ssl = ENV.fetch('PIA_FORCE_SSL', 'true') == 'true'
Rails.application.config.force_ssl  = force_ssl
Rails.application.config.assume_ssl = force_ssl
Rails.application.routes.default_url_options[:protocol] = force_ssl ? 'https' : 'http'

# DEFAULT_HOST peut contenir un port (ex. localhost:8080) : pia-back force port: nil,
# ce qui le supprimerait des URLs de pièces jointes.
if ENV['DEFAULT_HOST'].to_s.include?(':')
  host, port = ENV['DEFAULT_HOST'].split(':', 2)
  Rails.application.routes.default_url_options.merge!(host: host, port: port.to_i)
end

# --- E-mails -----------------------------------------------------------------
# pia-back envoie les liens d'activation de compte en synchrone. Sans SMTP, on
# écrit les mails dans tmp/mails (volume) au lieu de provoquer une erreur 500.
# on_load : appliqué après la config ActionMailer de Rails, qui sinon nous écrase.
ActiveSupport.on_load(:action_mailer) do
  if ENV['SMTP_ADDRESS'].present?
    self.delivery_method = :smtp
    self.smtp_settings = {
      address: ENV['SMTP_ADDRESS'],
      port: ENV.fetch('SMTP_PORT', 25).to_i,
      domain: ENV['SMTP_DOMAIN'],
      user_name: ENV['SMTP_USERNAME'].presence,
      password: ENV['SMTP_PASSWORD'].presence,
      authentication: ENV['SMTP_AUTHENTICATION'].presence&.to_sym,
      enable_starttls_auto: ENV.fetch('SMTP_ENABLE_STARTTLS_AUTO', 'true') == 'true'
    }.compact
  else
    self.delivery_method = :file
    self.file_settings = { location: Rails.root.join('tmp/mails') }
  end
end

# ApplicationMailer lit l'expéditeur dans les credentials Rails (absents ici).
Rails.application.config.to_prepare do
  from = ENV['EMAIL_FROM'].presence || Rails.application.credentials.email_from.presence || 'pia@localhost'
  ApplicationMailer.default from: from
end
