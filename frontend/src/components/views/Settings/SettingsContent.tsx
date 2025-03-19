import React from 'react';
import OrganizationSettings from './sections/OrganizationSettings';
import PermissionsSettings from './sections/PermissionsSettings';

interface SettingsContentProps {
  currentSection: string;
}

const SettingsContent = ({ currentSection }: SettingsContentProps) => {
  return (
    <div className="flex-1 overflow-auto">
      <div className="max-w-4xl mx-auto p-6">
        {currentSection === 'organization' && <OrganizationSettings />}
        {currentSection === 'permissions' && <PermissionsSettings />}
      </div>
    </div>
  );
};

export default SettingsContent;