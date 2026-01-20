"""Alat Kontrol Konkurensi (Versi Optimasi)

Peningkatan Performa:
1. Batas konkurensi dinamis (berdasarkan beban sistem)
2. Pemisahan kontrol konkurensi untuk berbagai jenis verifikasi
3. Mendukung jumlah konkurensi yang lebih tinggi
4. Pemantauan beban dan penyesuaian otomatis
"""
import asyncio
import logging
from typing import Dict
import psutil

logger = logging.getLogger(__name__)

# Menghitung jumlah konkurensi maksimum secara dinamis
def _calculate_max_concurrency() -> int:
    """Menghitung jumlah konkurensi maksimum berdasarkan sumber daya sistem"""
    try:
        cpu_count = psutil.cpu_count() or 4
        memory_gb = psutil.virtual_memory().total / (1024 ** 3)
        
        # Berdasarkan kalkulasi CPU dan Memori
        # Setiap inti CPU mendukung 3-5 tugas konkurensi
        # Setiap GB memori mendukung 2 tugas konkurensi
        cpu_based = cpu_count * 4
        memory_based = int(memory_gb * 2)
        
        # Ambil nilai terkecil dari keduanya, dan tetapkan batas atas/bawah
        max_concurrent = min(cpu_based, memory_based)
        max_concurrent = max(10, min(max_concurrent, 100))  # Antara 10-100
        
        logger.info(
            f"Sumber daya sistem: CPU={cpu_count}, Memori={memory_gb:.1f}GB, "
            f"Jumlah konkurensi yang dihitung={max_concurrent}"
        )
        
        return max_concurrent
    except Exception as e:
        logger.error(f"Gagal menghitung batas konkurensi: {e}")
        return 20  # Nilai default jika gagal

# Batas konkurensi global
MAX_CONCURRENT_TASKS = _calculate_max_concurrency()

# Semaphore untuk berbagai jenis verifikasi
_semaphores: Dict[str, asyncio.Semaphore] = {}

def get_verification_semaphore(verify_type: str) -> asyncio.Semaphore:
    """Mendapatkan semaphore berdasarkan jenis verifikasi"""
    if verify_type not in _semaphores:
        # Mengatur batas yang berbeda untuk jenis verifikasi yang berbeda
        # Verifikasi Spotify/YouTube biasanya lebih berat, batasnya lebih kecil
        if verify_type in ["spotify_student", "youtube_student"]:
            limit = max(2, int(MAX_CONCURRENT_TASKS * 0.3))
        else:
            limit = max(3, int(MAX_CONCURRENT_TASKS * 0.5))
            
        _semaphores[verify_type] = asyncio.Semaphore(limit)
        logger.info(f"Membuat semaphore untuk {verify_type}: limit={limit}")
        
    return _semaphores[verify_type]

async def monitor_system_load():
    """Memantau beban sistem saat ini"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    return {
        'cpu_percent': cpu_percent,
        'memory_percent': memory.percent,
        'max_concurrent': MAX_CONCURRENT_TASKS
    }

def adjust_concurrency_limits(factor: float):
    """Menyesuaikan semua batas konkurensi berdasarkan faktor tertentu"""
    global MAX_CONCURRENT_TASKS
    MAX_CONCURRENT_TASKS = max(10, int(MAX_CONCURRENT_TASKS * factor))
    
    for verify_type, sem in _semaphores.items():
        # Catatan: asyncio.Semaphore tidak mendukung perubahan value secara langsung
        # Di sini kita hanya mencatat log, penyesuaian sebenarnya akan dilakukan pada pembuatan berikutnya
        logger.info(f"Saran penyesuaian batas untuk {verify_type}: factor={factor}")

_monitor_task = None

async def start_load_monitoring(interval: int = 60):
    """Memulai tugas pemantauan beban sistem"""
    global _monitor_task
    
    if _monitor_task is not None:
        return
    
    async def monitor_loop():
        while True:
            try:
                await asyncio.sleep(interval)
                
                load_info = await monitor_system_load()
                cpu = load_info['cpu_percent']
                memory = load_info['memory_percent']
                
                logger.info(
                    f"Beban sistem: CPU={cpu:.1f}%, Memori={memory:.1f}%"
                )
                
                # Penyesuaian otomatis batas konkurensi
                if cpu > 80 or memory > 85:
                    # Beban terlalu tinggi, turunkan konkurensi
                    adjust_concurrency_limits(0.7)
                    logger.warning("Beban sistem terlalu tinggi, menurunkan batas konkurensi")
                elif cpu < 40 and memory < 60:
                    # Beban rendah, bisa naikkan konkurensi
                    adjust_concurrency_limits(1.2)
                    logger.info("Beban sistem rendah, meningkatkan batas konkurensi")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Terjadi kesalahan pada pemantauan beban: {e}")
    
    _monitor_task = asyncio.create_task(monitor_loop())
    logger.info(f"Pemantauan beban telah dimulai: interval={interval}s")


async def stop_load_monitoring():
    """Menghentikan tugas pemantauan beban sistem"""
    global _monitor_task
    
    if _monitor_task is not None:
        _monitor_task.cancel()
        try:
            await _monitor_task
        except asyncio.CancelledError:
            pass
        _monitor_task = None
        logger.info("Pemantauan beban telah dihentikan")