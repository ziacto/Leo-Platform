package com.rohit2810.leo_kotlin.repository

import android.content.Context
import com.rohit2810.leo_kotlin.database.getDatabase
import com.rohit2810.leo_kotlin.models.map.HeatmapDatabaseModule
import com.rohit2810.leo_kotlin.models.map.asDatabaseModule
import com.rohit2810.leo_kotlin.models.news.UnsafeNews
import com.rohit2810.leo_kotlin.models.news.asDatabaseModule
import com.rohit2810.leo_kotlin.network.MineApi
import com.rohit2810.leo_kotlin.utils.getLatitudeFromCache
import com.rohit2810.leo_kotlin.utils.getLongitudeFromCache
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import timber.log.Timber
import kotlin.random.Random

class HeatmapsRepository private constructor(var context: Context) {
    private val service = MineApi.retrofitService(context)
    private val database = getDatabase(context).heatmapDao

    suspend fun insertHeatmaps(latitude: Double, longitude: Double) {
        withContext(Dispatchers.IO) {
            try {
                var def = service.getHeatmaps(latitude, longitude)
                Timber.d(def.toString())
                val n = def.size
                if(database.getAllHeatmaps().value?.size !== 10) {
                    database.deleteAllHeatmaps()
                    generateHeatmaps(n)
                    def.map { it ->
                        Timber.d(
                            "Your location: ${it.loc.coordinates.get(0)}, ${it.loc.coordinates.get(
                                1
                            )}"
                        )
                        database.insertHeattmap(it.asDatabaseModule())
                    }
                }
            } catch (e: Exception) {
                Timber.d(e.localizedMessage)
                if(database.getAllHeatmaps().value?.size !== 10) {
                    database.deleteAllHeatmaps()
                    generateHeatmaps(0)
                }
            }

        }
    }

    suspend fun getDirections(lat1: Double, long1: Double, lat2: Double, long2: Double) {
        database.deleteAllDirections()
        var list = service.getDirections(lat1, long1, lat2, long2)
        var newList = list.asDatabaseModule()
        for (route in newList) {
            database.insertDirections(route)
        }
        getUnsafe()
    }

    suspend fun getUnsafe() {
        database.deleteAllUnsafe()
        var list  = service.getUnsafe().news
        var i = 0
        for (ele in list) {
            Timber.d(ele.toString())
            ele.Latitude += 0.008
            ele.Longitude += 0.008
            Timber.d(ele.toString())
            database.insertUnsafe(ele.asDatabaseModule())
        }
    }

    private suspend fun generateHeatmaps(n: Int) {
        var n1 = n
        while (n1 < 10) {
            var random = (-1000..1000).random()
            var lat = getLatitudeFromCache(context).toDouble() + (random * 0.0002)
            random = (-1000..1000).random()
            var long = getLongitudeFromCache(context).toDouble() + random * 0.0002
            var count = (1..50).random()
            database.insertHeattmap(HeatmapDatabaseModule(count, lat, long))
            n1++
        }
    }

    companion object {
        private lateinit var INSTANCE: HeatmapsRepository

        fun getInstance(context: Context): HeatmapsRepository {
            synchronized(HeatmapsRepository::class.java) {
                if (!::INSTANCE.isInitialized) {
                    INSTANCE = HeatmapsRepository(context)
                }
            }
            return INSTANCE
        }
    }
}