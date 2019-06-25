# -*- coding: utf-8 -*-
'''
Genetic algorithm to find the first Lyapunov coefficient required for a -3dB
point at +/- 1 to 50Hz from the detector frequency.

See run_lyapunov_bandwidth_ga.py and run_amplitude_ga.py for implementations.
'''

import numpy as np
from detectorbank import DetectorBank
from deap import base, creator, tools
from collections import deque
import inflect


class GA:
    
    def __init__(self, GAResultsPath, f0, sr, bandwidth, damping, amp, seed, 
                 seedvar, term):
        """ Make GA object
        
            Parameters
            ----------
            GAResultsPath : str
                File to write genetic alorithm log to
            f0 : float
                Centre frequency to test
            sr : int
                Sample rate
            bandwidth : float
                Target bandwidth
            damping : float
                Damping factor
            amp : float
                Input amplitude
            seed : float
                Estimated fLc value to seed the initial population with
            seedvar : float
                Proportion by which 'seed' can vary by either way
            term : float
                Terminate when fitness is within  this value
        """
        
        self._initGA(seed, seedvar, term)
        
        self.f0 = f0
        self.sr = sr
        dur = 3 # make 3 seconds of audio
        self.audio = self._make_input(f0, sr, dur)
        self.audio *= amp
        
        # frequency difference
        self.fd = bandwidth/2
        
        # DetectorBank parameters
        # DetectorBank parameters
        method = DetectorBank.runge_kutta
        f_norm = DetectorBank.freq_unnormalized
        a_norm = DetectorBank.amp_unnormalized
        gain = 1
        self.dbp = (method|f_norm|a_norm, damping, gain)
        
        self.outfile = open(GAResultsPath, 'w')
        self.outfile.write('Frequency difference: {:.0f}Hz\n\n'.format(self.fd))
        
    
    def _initGA(self, seed, seedvar, term):
        ## intialise Genetic Algorithm objects and parameters
        ## GA log will be written to 'resultspath'
        
        creator.create('FitnessFunc', base.Fitness, weights=(-1.0,))
        creator.create('Individual', list, fitness=creator.FitnessFunc)
        
        self.toolbox = base.Toolbox()
        
        # how to make a population of individuals, each initialised with
        # attributes from _attr()
        self.toolbox.register('attr', self._attr, seed, seedvar)
        self.toolbox.register('individual', tools.initRepeat, 
                              creator.Individual, self.toolbox.attr, 1)
        self.toolbox.register('population', tools.initRepeat, list, 
                              self.toolbox.individual)
        
        # population size
        self.popSize = 120
        
        # set generation count to zero
        self.gen = 0
        
        # probability that an individual will be selected for crossover/mutation
        self.cxpb = 0.5
        self.mutpb = 0.5
        # termination criterion, i.e. stop when fitness is within 0.01dB of -3
        self.term = term #0.01 #0.02
        # keep fitnesses in a deque, so that we can see if it stops improving
        self.fits_size = 5
        self.fits = deque(maxlen=self.fits_size)
        # max number of generations
        self.mxgen = 50
        # tournament selection, blended crossover, Gaussian mutation
        self.toolbox.register('select', tools.selTournament, tournsize=3)
        self.toolbox.register('crossover', tools.cxBlend, alpha=0.7)
        self.toolbox.register('mutate', tools.mutGaussian, indpb=0.1)


    @staticmethod
    def _make_input(f0, sr, dur):
        # mak sine tone
        t = np.linspace(0, 2*np.pi*f0*dur, sr*dur)
        audio = np.sin(t)
        audio = np.append(audio, np.zeros(sr))
        return audio


    @staticmethod
    def _attr(value, var):
        """ Return a random number, within +/- `var` of `value`
        
            Parameters
            ----------
            value : float
                seed value
            var : float
                proportional limit on how much `value` can vary in each 
                direction. Must be between 0 and 1 (i.e. between 0 and 100%).
                
            Returns
            -------
            out : float
                Random number, within +/- `var` of `value`
        """
        
        if not 0 <= var <= 1:
            raise ValueError("'var' must be between 0 and 1")
         
        # get minimum and maximum output value
        mn = value * (1-var)
        mx = value * (1+var)
        
        # make random float between 0 and 1
        rand = np.random.random()
        
        # get number 100*r% between mn and mx
        out = (mx - mn) * rand + mn
        
        return out
    
    
    def terminate(self):
        
        # current fitness is most recent value in deque
        fit = self.fits[-1]
        
        funcs = [np.less_equal, np.greater_equal]
        fitWeights = creator.FitnessFunc.weights
        for w in fitWeights:
            if np.sign(w) == -1:
                func = funcs[0]
            else:
                func = funcs[1]
        
        return func(fit, self.term)
    
    
    def fitline(self):
        # return False if fitnesses are improving
        # return True if previous fitnesses are within 99% of each other
        # (i.e. fitness is flatlining)
        
        if len(self.fits) == self.fits_size:
            mn = min(self.fits)
            mx = max(self.fits)
            if mn/mx >= 0.99:
                return True
            else:
                return False
    
    
    def _get_abs_z(self, freq, flc):
        # make a DetectorBank with the given parameters and return |z|
        
        size = len(freq)
        bw = np.zeros(size)
        bw.fill(flc)
        
        det_char = np.array(list(zip(freq, bw)))
        
        # NB have changed DetectorBank code to regard det_char as freq,fLc 
        # pairs instead of freq,bw pairs
        # all that is required to do this is change AbstractDetector::getLyapunov
        # to simply return the value it is passed
        # i.e. we pretend that 'bandwidth' values are Lyapunov coeff
        det = DetectorBank(self.sr, self.audio.astype(np.float32), 0, 
                           det_char, *self.dbp)
        
        # get output
        z = np.zeros((size,len(self.audio)), dtype=np.complex128)
        r = np.zeros(z.shape)
        det.getZ(z,size)
        det.absZ(r, z)
        
        return r
    
    
    def _evaluate(self, individual):
        ''' Evaluate an individual's fitness 
            
            Parameters
            ----------
            individual : list
                one element list, containing the first Lyapunov coefficient to
                be tested
                
            Returns
            -------
            fitness : tuple 
                the average difference from -3dB of the detectors at +/-fd
        '''
        
        flc = individual[0]
        
        # if candidate first Lyapunov coefficient is positive, return a very
        # unfit fitness
        if flc > 0:
            return 1000,
        
#        print('Evaluating individual {}'.format(flc))
        
        # detector frequencies
        f = np.array([self.f0-self.fd, self.f0, self.f0+self.fd])
        
        # get DetectorBank responses
        r = self._get_abs_z(f, flc)
        
        # get max values in DB output
        maxima = np.array([np.max(resp) for resp in r])
        # normalise to centre freq amplitude
        maxima /= maxima[1]
        
        # convert maxima to decibels
        max_db = 20*np.log10(maxima)
        
#        print('Maxima: {} and {} dB'.format(max_db[0], max_db[2]))
        
        # fitness is how close maxima are to -3
        fit0 = abs(-3 - max_db[0])
        fit1 = abs(-3 - max_db[2])
        
        fitness = (fit0 + fit1) / 2
        
        return fitness,


    def _evaluatePop(self, pop):
        ## Evaluate a population
        ## Returns the population with fitness values set
        
        self.evalSize = len(pop)
        
        # set individual count to zero before evaluating population
        self.indCount = 0
        
        # evaluate the population
        fitnesses = list(map(self.toolbox.evaluate, pop))
        
        # set the fitness values for the population
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit
            
        return pop
    
    
    def _fitnessStats(self, pop):
        
         # gather all the fitnesses in one list and print the stats
        fits = [ind.fitness.values[0] for ind in pop]
        
        # print stats
        funcs = {'Min':np.min, 'Max':np.max, 'Avg':np.mean, 'Std':np.std}
        for name in funcs.keys():
            func = funcs[name]
            self.outfile.write('\t{}: {:.3f}\n'.format(name, func(fits)))
        self.outfile.write('\n')
        
        bestInd = tools.selBest(pop, 1)[0]
        fit = bestInd.fitness.values[0]
        
        msg = ('Best individual in this generation: {}, fitness: {:.6f}dB'
                .format(bestInd, fit))
        
        print(msg)
        
        return fit
    
    
    def evolve(self):
        """ Run the genetic algorithm 
        
            Returns
            -------
            bestInd : list
                Best individual found
            bestFit : float
                The fitness of the best individual
            ret : int
                Return code (see below)
            status : str
                String summarising the evolution
            
            Return codes
            ------------
            0 : An individual which met the given termination criterion was found
            
            1 : The maximum number of generations was reached
            
            2 : Fitness did not improve for several generations
        """
        
        # create a population of individuals
        pop = self.toolbox.population(n=self.popSize)
        
        # register evaluate function 
        # ('individual' is automatically sent as first arg)
        self.toolbox.register('evaluate', self._evaluate)
        
        # the following code is (mostly) from deap's onemax.py example:
        self.outfile.write('---- Start of evolution ----\n')
        print('Generation {}/{}             '.format(self.gen, self.mxgen))
        
        # initial evaluation of population
        pop = self._evaluatePop(pop)
        
        # size of an individual
        # (cannot get this until individuals are actually created in the 
        # population - cannot get it from toolbox.register stuff in init)
        indSize = len(pop[0])
        
        self.outfile.write('\tEvaluated {} individuals\n'.format(len(pop)))
        
        # print fitness stats and and get initial fitness
        fit = self._fitnessStats(pop)
        # store fitness in deque
        self.fits.append(fit)
        
        # gen 0 is the initial evaluation
        self.gen += 1
        # begin the evolution
        # while term criterion has not been met, fitnesses are improving 
        # and haven't reached max no. of generations
        while (not self.terminate() and not self.fitline() 
               and self.gen < self.mxgen):
            
            print('Generation {}/{}             '.format(self.gen, self.mxgen))
            self.outfile.write('---- Generation {} ----\n'.format(self.gen))
            
            # select the next generation individuals
            offspring = self.toolbox.select(pop, len(pop))
            # clone the selected individuals
            offspring = list(map(self.toolbox.clone, offspring))
        
            # apply crossover and mutation on the offspring
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
    
                # cross two individuals with probability cxpb
                if np.random.random() < self.cxpb:
                    self.toolbox.crossover(child1, child2)
    
                    # fitness values of the children
                    # must be recalculated later
                    del child1.fitness.values
                    del child2.fitness.values
    
            for mutant in offspring:
    
                # mutate an individual with probability mutpb
                if np.random.random() < self.mutpb:
                    # need fLc to be negative, so set mu big and -ve
                    self.toolbox.mutate(mutant, mu=[-175]*indSize, 
                                        sigma=[40]*indSize)
                    del mutant.fitness.values
        
            # evaluate the individuals with an invalid fitness
            # (ie new individuals)
            invalidInd = [ind for ind in offspring if not ind.fitness.valid]
            invalidInd = self._evaluatePop(invalidInd)
            
            self.outfile.write('\tEvaluated {} individuals\n'
                               .format(len(invalidInd)))
            
            # replace population with offspring
            pop = offspring
            
            # print fitness stats, get max fitness
            fit = self._fitnessStats(pop)
            # append fitness to deque
            self.fits.append(fit)
            
            # increment generation counter
            self.gen += 1
        
        # end of evolution
        self.outfile.write('---- End of evolution ----\n\n')
        
        bestInd = tools.selBest(pop, 1)[0]
        bestFit = bestInd.fitness.values[0]
        
        ret, status = self._get_return_code()
        
        status = status.format(bestInd, bestFit)
        
        print(status)
             
        self.outfile.write(status)
        self.outfile.close()
        
        return bestInd, bestFit, ret, status
    
    
    def _get_return_code(self):
        # Non-zero return code means the GA terminated without finding an
        # individual which met the termination criterion
        
        if self.terminate():
            ret = 0
            status = 'Found best individual: {}, fitness: {}dB\n'
            
        elif self.gen >= self.mxgen:
            ret = 1
            status = 'Reached maximum number of generations.\n'
            status += 'Best individual so far is {}, fitness: {}dB\n'
        
        elif self.fitline():
            ret = 2
            p = inflect.engine()
            num = p.number_to_words(self.fits_size)
            status = "Fitness hasn't improved for {} generations. ".format(num)
            status += "Terminating.\n"
            status += 'Best individual so far is {}, fitness: {}dB\n'

        status = 'GA terminated with code {}\n'.format(ret) + status
        
        return ret, status
    
    
def write_summary(bestVals, path, header):
    ''' Write csv file of bandwidth and error for each damping factor
    
        Parameters
        ----------
        bestVals : dict 
            Dictionary of key : (value, value) pairs
        path : str
            Path to write to
    '''

    outfile = open(path, 'w')
    outfile.write(header)
    
    for key, value in bestVals.items():  
        outfile.write('{},{},{},\n'.format(key, *value))
        
    outfile.close()
