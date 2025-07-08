// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	integrations: [
		starlight({
			title: 'Ebiose Documentation',
			social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/xabier/ebiose' }],
			sidebar: [
				{
					label: 'Guides',
					items: [
						{ label: 'Our Vision', slug: 'guides/our-vision' },
						{ label: 'Getting Started', slug: 'guides/getting-started' },
						{ label: 'Core Concepts', slug: 'guides/core-concepts' },
					],
				},
				{
					label: 'Reference',
					autogenerate: { directory: 'reference' },
				},
			],
		}),
	],
});
