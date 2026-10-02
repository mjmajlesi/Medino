import HeroSlider from '../components/Home/HeroSlider';
import QuickSearch from '../components/Home/QuickSearch';
import SectionCards from '../components/Home/SectionCards';
import StatsBar from '../components/Home/StatsBar';

export default function HomePage() {
  return (
    <>
      <HeroSlider />
      <QuickSearch />
      <StatsBar />
      <SectionCards />
    </>
  );
}
