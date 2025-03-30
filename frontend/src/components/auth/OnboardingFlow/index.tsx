import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../contexts/AuthContext';
import ProfileSetup from './steps/ProfileSetup';
import ContactInfo from './steps/ContactInfo';
import OrganizationSetup from './steps/OrganizationSetup';
import HubPermissions from './steps/HubPermissions';
import OnboardingVideo from './steps/OnboardingVideo';
import useRoleStore from '../../../store/roleStore';

type OnboardingStep = 'profile' | 'contact' | 'organization' | 'hubs' | 'video';

const OnboardingFlow = () => {
  const [currentStep, setCurrentStep] = useState<OnboardingStep>('profile');
  const { user } = useAuth();
  const [userData, setUserData] = useState({
    photoUrl: '',
    fullName: user?.fullName || '',
    email: user?.email || '',
    organizationName: '',
    organizationSize: '',
    industry: '',
  });
  const navigate = useNavigate();
  const { setRole } = useRoleStore();

  // Update userData when user data changes
  useEffect(() => {
    if (user) {
      setUserData(prev => ({
        ...prev,
        fullName: user.fullName || prev.fullName,
        email: user.email || prev.email,
      }));
    }
  }, [user]);

  const handleStepComplete = (step: OnboardingStep, data?: any) => {
    if (data) {
      setUserData(prev => ({ ...prev, ...data }));
    }

    switch (step) {
      case 'profile':
        // Skip contact info step and go directly to organization
        setCurrentStep('organization');
        break;
      case 'organization':
        setCurrentStep('hubs');
        break;
      case 'hubs':
        setCurrentStep('video');
        break;
      case 'video':
        // Set role and redirect to dashboard
        setRole('user');
        navigate('/dashboard');
        break;
    }
  };

  const handleSkipVideo = () => {
    setRole('user');
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
      <div className="w-full max-w-2xl">
        <AnimatePresence mode="wait">
          {currentStep === 'profile' && (
            <motion.div
              key="profile"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
            >
              <ProfileSetup onComplete={(data) => handleStepComplete('profile', data)} />
            </motion.div>
          )}


          {currentStep === 'organization' && (
            <motion.div
              key="organization"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
            >
              <OrganizationSetup 
                onComplete={(data) => handleStepComplete('organization', data)} 
              />
            </motion.div>
          )}

          {currentStep === 'hubs' && (
            <motion.div
              key="hubs"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
            >
              <HubPermissions onComplete={() => handleStepComplete('hubs')} />
            </motion.div>
          )}

          {currentStep === 'video' && (
            <motion.div
              key="video"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
            >
              <OnboardingVideo 
                onComplete={() => handleStepComplete('video')}
                onSkip={handleSkipVideo}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Progress Indicator */}
        <div className="mt-8 flex justify-center gap-2">
          {(['profile', 'organization', 'hubs', 'video'] as const).map((step, index) => (
            <div
              key={step}
              className={`w-2 h-2 rounded-full transition-colors ${
                currentStep === step
                  ? 'bg-emerald-400'
                  : index < ['profile', 'organization', 'hubs', 'video'].indexOf(currentStep)
                  ? 'bg-emerald-200'
                  : 'bg-gray-200'
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default OnboardingFlow;
