package com.rohit2810.leo_kotlin.ui.settings

import android.content.Intent
import android.os.Bundle
import androidx.fragment.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.core.content.ContextCompat
import androidx.lifecycle.Observer
import androidx.lifecycle.ViewModelProvider
import androidx.navigation.fragment.findNavController
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.WorkRequest
import com.rohit2810.leo_kotlin.databinding.FragmentSettingsBinding
import com.rohit2810.leo_kotlin.services.LocationService
import com.rohit2810.leo_kotlin.services.FallDetectionService
import com.rohit2810.leo_kotlin.services.wifidirect.WiFiP2PServiceLeo
import com.rohit2810.leo_kotlin.utils.getFallDetectionPrefs
import com.rohit2810.leo_kotlin.utils.getUserFromCache
import com.rohit2810.leo_kotlin.utils.saveFallDetectionPrefs
import com.rohit2810.leo_kotlin.utils.showToast
import com.rohit2810.leo_kotlin.work_request.StartScheduler
import timber.log.Timber
import java.util.concurrent.TimeUnit

class SettingsFragment : Fragment() {

    private lateinit var viewModel: SettingsViewModel
    private lateinit var settingsViewModelFactory: SettingsViewModelFactory

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {

        val binding = FragmentSettingsBinding.inflate(inflater, container, false)

        binding.lifecycleOwner = this

        settingsViewModelFactory = SettingsViewModelFactory(requireActivity().applicationContext)

        requireActivity().title = "Settings"
//        var activity = activity as AppCompatActivity
//        activity.supportActionBar?.setDisplayHomeAsUpEnabled(true)

        viewModel = ViewModelProvider(this, settingsViewModelFactory).get(SettingsViewModel::class.java)

        binding.viewmodel = viewModel
        binding.switchFall.isChecked = getFallDetectionPrefs(activity?.applicationContext!!)

        viewModel.navigateToEmergencyContacts.observe(viewLifecycleOwner, Observer {
            it?.let {
                Timber.d("Entered")
                this.findNavController().navigate(
                    SettingsFragmentDirections.actionSettingsFragmentToEmergencyContactsFragment2(
                    getUserFromCache(activity?.applicationContext!!)!!, true
                ))
                viewModel.doneGoToEmergencyContacts()
            }
        })

        viewModel.navigateToLogin.observe(viewLifecycleOwner, Observer {
            it?.let {
                stopService()

                this.findNavController().navigate(SettingsFragmentDirections.actionSettingsFragmentToLoginFragment())
                viewModel.doneNavigateToLogin()
            }
        })

        viewModel.snackbarMsg.observe(viewLifecycleOwner, Observer {
            it?.let {
                activity?.showToast(it)
                viewModel.doneShowingSnackbarMsg()
            }
        })

        viewModel.toggleFallDetection.observe(viewLifecycleOwner, Observer {
            it?.let {
                if (!getFallDetectionPrefs(activity?.applicationContext!!)) {
                    startFallDetectionService()
                    activity?.showToast("Fall detection service enabled")
                }else {
                    stopFallDetectionService()
                    activity?.showToast("Fall detection service disabled")
                }
                saveFallDetectionPrefs(activity?.applicationContext!!)
                viewModel.doneToggleFallDetection()
            }
        })

        viewModel.goToAboutUs.observe(viewLifecycleOwner, Observer {
            it?.let {
                this.findNavController().navigate(SettingsFragmentDirections.actionSettingsFragmentToAboutFragment())
                viewModel.doneGoToAboutUs()
            }
        })

//        viewModel.fallDetectionService.observe(viewLifecycleOwner,  Observer{
//            it?.let {
//
//                viewModel.doneFallDetectionScheduling()
//            }
//        })

//        //Work Manager Request
//        val workRequest = PeriodicWorkRequestBuilder<StartScheduler>(10, TimeUnit.MINUTES)
//            .setInitialDelay(20, TimeUnit.SECONDS).addTag("FALL_DETECTION_START").build()
//
//        WorkManager.getInstance(requireContext())
//            .enqueueUniquePeriodicWork("FALL_DETECTION_START", ExistingPeriodicWorkPolicy.REPLACE, workRequest);



        // Inflate the layout for this fragment
        return binding.root
    }

    fun stopService() {
        stopFallDetectionService()
        val intent2 = Intent(activity?.applicationContext!!, LocationService::class.java)
        activity?.stopService(intent2)
        val intent3 = Intent(activity?.applicationContext!!, WiFiP2PServiceLeo::class.java)
        activity?.stopService(intent3)
    }

    fun startFallDetectionService() {
        val intent = Intent(activity?.applicationContext, FallDetectionService::class.java)
        ContextCompat.startForegroundService(activity?.applicationContext!!, intent)
    }

    fun stopFallDetectionService() {
        val intent = Intent(activity?.applicationContext!!, FallDetectionService::class.java)
        activity?.stopService(intent)
    }


}