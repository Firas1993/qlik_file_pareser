module.exports = {
  apps: [
    {
      name: 'monthly-workflow',
      script: './run_monthly_workflow.sh',
      interpreter: 'bash',
      cwd: '.',
      instances: 1,
      autorestart: false,
      watch: false,
      merge_logs: true,
      output: './logs/out.log',
      error: './logs/err.log',
      log_date_format: 'YYYY-MM-DD HH:mm Z'
    }
  ]
};
