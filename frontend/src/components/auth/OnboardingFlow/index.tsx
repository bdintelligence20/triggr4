import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import ProfileSetup from './steps/ProfileSetup';
import ContactInfo from './steps/ContactInfo';
import HubPermissions from './steps/HubPermissions';
import OnboardingVideo from './steps/OnboardingVideo';
import useRoleStore from '../../../store/roleStore';

type OnboardingStep = 'profile' | 'contact' | 'hubs' | 'video';

const OnboardingFlow = () => {
  const [currentStep, setCurrentStep] = useState<OnboardingStep>('profile');
  const [userData, setUserData] = useState({
    photoUrl: '',
    fullName: '',
    email: '',
    whatsapp: '',
  });
  const navigate = useNavigate();
  const { setRole } = useRoleStore();

  const handleStepComplete = (step: OnboardingStep, data?: any) => {
    if (data) {
      setUserData(prev => ({ ...prev, ...data }));
    }

    switch (step) {
      case 'profile':
        setCurrentStep('contact');
        break;
      case 'contact':
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

          {currentStep === 'contact' && (
            <motion.div
              key="contact"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
            >
              <ContactInfo 
                initialData={userData}
                onComplete={(data) => handleStepComplete('contact', data)} 
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
          {(['profile', 'contact', 'hubs', 'video'] as const).map((step, index) => (
            <div
              key={step}
              className={`w-2 h-2 rounded-full transition-colors ${
                currentStep === step
                  ? 'bg-emerald-400'
                  : index < ['profile', 'contact', 'hubs', 'video'].indexOf(currentStep)
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