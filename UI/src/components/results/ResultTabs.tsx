import { useState } from 'react';
import { Tab } from '@headlessui/react';
import { SearchResult } from '../../types/search';

// Components
import SocialMediaSection from './SocialMediaSection';
import PEPSection from './PEPSection';
import MediaSection from './MediaSection';
import RiskAssessment from './RiskAssessment';
import SourcesSection from './SourcesSection';
import RawDataSection from './RawDataSection';

// Icons
import { 
  UserGroupIcon, 
  DocumentTextIcon, 
  NewspaperIcon, 
  ShieldExclamationIcon,
  ServerIcon,
  CodeBracketIcon
} from '@heroicons/react/24/outline';

interface ResultTabsProps {
  result: SearchResult;
}

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ');
}

const ResultTabs = ({ result }: ResultTabsProps) => {
  const [selectedTab, setSelectedTab] = useState(0);
  
  const tabs = [
    { name: 'Social Media', icon: UserGroupIcon },
    { name: 'PEP & Sanctions', icon: ShieldExclamationIcon },
    { name: 'Media Coverage', icon: NewspaperIcon },
    { name: 'Risk Assessment', icon: DocumentTextIcon },
    { name: 'Sources', icon: ServerIcon },
    { name: 'Raw Data', icon: CodeBracketIcon }
  ];
  
  const hasSocialMedia = Object.keys(result.social_media_profiles || {}).length > 0;
  const hasPEP = (result.pep_records || []).length > 0;
  const hasMedia = (result.news_articles || []).length > 0;
  
  return (
    <div className="px-4 py-5 sm:px-6">
      <Tab.Group selectedIndex={selectedTab} onChange={setSelectedTab}>
        <Tab.List className="flex border-b border-gray-200">
          {tabs.map((tab, index) => (
            <Tab
              key={tab.name}
              className={({ selected }) =>
                classNames(
                  'py-4 px-4 text-sm font-medium text-center whitespace-nowrap focus:outline-none',
                  'flex items-center space-x-2',
                  selected
                    ? 'border-b-2 border-indigo-600 text-indigo-600'
                    : 'border-b-2 border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                )
              }
            >
              <tab.icon className="h-5 w-5" />
              <span>{tab.name}</span>
              
              {/* Show count badges for relevant tabs */}
              {index === 0 && hasSocialMedia && (
                <span className="ml-2 px-2 py-0.5 rounded-full text-xs bg-indigo-100 text-indigo-800">
                  {Object.values(result.social_media_profiles || {}).flat().length}
                </span>
              )}
              {index === 1 && hasPEP && (
                <span className="ml-2 px-2 py-0.5 rounded-full text-xs bg-indigo-100 text-indigo-800">
                  {(result.pep_records || []).length}
                </span>
              )}
              {index === 2 && hasMedia && (
                <span className="ml-2 px-2 py-0.5 rounded-full text-xs bg-indigo-100 text-indigo-800">
                  {(result.news_articles || []).length}
                </span>
              )}
            </Tab>
          ))}
        </Tab.List>
        
        <Tab.Panels className="mt-4">
          <Tab.Panel>
            <SocialMediaSection profiles={result.social_media_profiles || {}} />
          </Tab.Panel>
          
          <Tab.Panel>
            <PEPSection records={result.pep_records || []} />
          </Tab.Panel>
          
          <Tab.Panel>
            <MediaSection articles={result.news_articles || []} />
          </Tab.Panel>
          
          <Tab.Panel>
            <RiskAssessment result={result} />
          </Tab.Panel>
          
          <Tab.Panel>
            <SourcesSection 
              sources={result.sources_checked || []} 
              successful={result.sources_successful || []} 
            />
          </Tab.Panel>
          
          <Tab.Panel>
            <RawDataSection result={result} />
          </Tab.Panel>
        </Tab.Panels>
      </Tab.Group>
    </div>
  );
};

export default ResultTabs;