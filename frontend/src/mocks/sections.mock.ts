import type { Section } from '../types/models';

export const sectionsMock: Section[] = [
  { id: 'sec-basic', slug: 'basic', title: 'علوم پایه', description: 'آناتومی، بیوشیمی، فیزیولوژی و دروس پایه' },
  { id: 'sec-physio', slug: 'physio', title: 'فیزیوپاتولوژی', description: 'پاتولوژی و فارماکولوژی دستگاه‌ها' },
  { id: 'sec-karamozi', slug: 'karamozi', title: 'کارآموزی', description: 'آموزش بالینی مقدماتی و سمیولوژی' },
  { id: 'sec-karvarzi', slug: 'karvarzi', title: 'کارورزی (اینترنی)', description: 'بخش‌های داخلی، جراحی و کشیک‌ها' },
  { id: 'sec-stage', slug: 'stage', title: 'استاژری', description: 'استاژرهای تخصصی اطفال، زنان و...' },
  { id: 'sec-general', slug: 'general', title: 'دروس عمومی', description: 'زبان، اخلاق پزشکی و دروس عمومی' },
];
