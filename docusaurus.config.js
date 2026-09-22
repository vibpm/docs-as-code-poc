// @ts-check

const config = {
  title: 'Regulatory Content Platform',
  tagline: 'Docs-as-Code / Single Source of Truth PoC',

  url: process.env.SITE_URL || 'http://localhost:8080',
  baseUrl: '/',

  onBrokenLinks: 'warn',

  favicon: 'img/favicon.ico',

  organizationName: 'client',
  projectName: 'docs-as-code',

  presets: [
    [
      'classic',
      {
        docs: {
          path: 'generated/docs',
          routeBasePath: '/',
          sidebarPath: require.resolve('./sidebars.js')
        },
        blog: false,
        theme: {
          customCss: require.resolve('./src/css/custom.css')
        }
      }
    ]
  ],

  themeConfig: {
    navbar: {
      title: 'Regulatory Content',
      items: [
        {
          href: `${process.env.SITE_URL || 'http://localhost:8080'}/admin/`,
          label: 'Редактировать',
          position: 'right'
        }
      ]
    },
    footer: {
      style: 'dark',
      copyright:
        `Docs-as-Code PoC — build ${process.env.CI_COMMIT_SHORT_SHA || 'local'}`
    }
  }
};

module.exports = config;
